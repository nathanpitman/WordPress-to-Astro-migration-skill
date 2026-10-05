import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Model, Status } from '../types'

// What the wp-to-astro skill keeps current in docs/run-state.json (policies/run-state.md).
const RUN_STATE = 'docs/run-state.json'

const model = atom({ plugin: 'wordpress-to-astro-progress', key: 'model' } as const, null)
const active = atom({ plugin: 'wordpress-to-astro-progress', key: 'active' } as const, false)
const isHidden = atom({ plugin: 'wordpress-to-astro-progress', key: 'isHidden' } as const, false)

// The five stages and the phases (steps) each is made of, in the order the skill runs them.
const STAGES: { n: number; name: string; phases: { key: string; label: string }[] }[] = [
  { n: 1, name: 'Discover', phases: [{ key: '0', label: 'Intake' }, { key: '1', label: 'Crawl' }, { key: '2', label: 'Unlinked' }, { key: 'smoke', label: 'Smoke slice' }] },
  { n: 2, name: 'Analyse', phases: [{ key: '3', label: 'Content' }, { key: '4', label: 'Forms' }, { key: '7', label: 'SEO' }, { key: '10', label: 'A11y' }, { key: '11', label: 'Errors' }] },
  { n: 3, name: 'Build', phases: [{ key: '5', label: 'Layouts' }, { key: '6', label: 'CSS' }, { key: '9', label: 'Assets' }, { key: '8', label: 'Listings' }] },
  { n: 4, name: 'Verify', phases: [] },
  { n: 5, name: 'Finish', phases: [{ key: '12', label: 'Build+README' }] },
]
const COUNTED = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
const SKILL = /^(wp-to-astro|wordpress-to-astro)$/

// Free-text statuses ("done", "inventory done", "in-progress", "stale", ...) reduced to four.
const status = (v: unknown): Status => {
  const s = String(v ?? '').toLowerCase()
  if (s.includes('stale')) return 'stale'
  if (s.includes('progress')) return 'doing'
  if (s.includes('done') || s === 'complete') return 'done'
  return 'todo'
}

const parse = (text: string): Model | null => {
  try {
    const j = JSON.parse(text)
    const stage = Number(j.stage) || 1
    const stages = [1, 2, 3, 4, 5].map((n): Status => {
      const s = status(j.stages?.[String(n)])
      return s === 'todo' && n === stage ? 'doing' : s
    })
    const phases: Record<string, Status> = {}
    for (const [k, v] of Object.entries(j.phases ?? {})) phases[k] = status(v)
    const open = Array.isArray(j.decisions) ? j.decisions.filter((d: { status?: string }) => d?.status === 'open').length : 0
    return { domain: String(j.domain ?? ''), stage, stages, phases, openDecisions: open }
  } catch {
    return null
  }
}

const GLYPH: Record<Status, string> = { done: '✓', doing: '●', stale: '↻', todo: '○' }
const COLOR: Record<Status, string | undefined> = { done: 'green', doing: 'yellow', stale: 'magenta', todo: undefined }

// Re-reads docs/run-state.json (relative to the session's working directory) into the band's state.
async function refresh($: any) {
  if (!(await $.fs.exists(RUN_STATE))) return
  const next = parse(await $.fs.read(RUN_STATE))
  await update($, model, () => next)
  if (next) await update($, active, () => true)
}

export const register: Register = on => {
  let stop: (() => void) | undefined

  on('session.start', async ($, e, next) => {
    await refresh($).catch(() => undefined)
    stop?.()
    // The skill and its scripts write run-state.json from the shell, so poll as well as react to turns.
    stop = $.clock.every(5000, () => void refresh($).catch(() => undefined))
    return next(e)
  })

  // Invoking the skill (typed as /wp-to-astro or through the Skill tool) switches the band on, even before a run exists.
  on('skill.prompt', async ($, e, next) => {
    if (SKILL.test(e.skill)) await update($, active, () => true)
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    await refresh($).catch(() => undefined)
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const on_ = await read($, active)
    if (e.props.hasSurvey || !on_) return next(e)
    const m = await read($, model)
    const hidden = await read($, isHidden)
    const { Box, Button, Text } = $.ui.resolve(e)

    if (hidden) {
      return <Box><Button key="show" label="wp-to-astro progress" onPress={() => update($, isHidden, () => false)} /></Box>
    }

    // Skill invoked but no run-state.json yet: show the five stages as not started.
    const stages: Status[] = m?.stages ?? ['todo', 'todo', 'todo', 'todo', 'todo']
    const stage = m?.stage ?? 1
    const doneCount = m ? COUNTED.filter(k => m.phases[k] === 'done').length : 0
    const filled = Math.round((doneCount / COUNTED.length) * 20)
    const current = STAGES.find(s => s.n === stage)!

    return (
      <Box flexDirection="column">
        <Box>
          <Text bold color="cyan">wp-to-astro </Text>
          <Text dimColor>{m?.domain ? `· ${m.domain} · ` : '· waiting for intake · '}</Text>
          <Text color="green">{'█'.repeat(filled)}</Text>
          <Text dimColor>{'░'.repeat(20 - filled)}</Text>
          <Text dimColor>{` ${doneCount}/${COUNTED.length} phases`}</Text>
          {m && m.openDecisions > 0 ? <Text color="yellow">{`  ${m.openDecisions} open decision${m.openDecisions === 1 ? '' : 's'}`}</Text> : null}
          <Text dimColor> </Text>
          <Button key="hide" label="Hide" onPress={() => update($, isHidden, () => true)} />
        </Box>
        <Box>
          {STAGES.map((s, i) => (
            <Text key={s.n} bold={s.n === stage} color={COLOR[stages[i]]} dimColor={stages[i] === 'todo' && s.n !== stage}>
              {`${i ? '  ›  ' : ''}${GLYPH[stages[i]]} ${s.n} ${s.name}`}
            </Text>
          ))}
        </Box>
        {current.phases.length ? (
          <Box>
            <Text dimColor>{`Stage ${stage} phases:  `}</Text>
            {current.phases.map((p, i) => {
              const st: Status = m?.phases[p.key] ?? 'todo'
              return <Text key={p.key} color={COLOR[st]} dimColor={st === 'todo'}>{`${i ? '   ' : ''}${GLYPH[st]} ${p.label}`}</Text>
            })}
          </Box>
        ) : null}
      </Box>
    )
  })
}
