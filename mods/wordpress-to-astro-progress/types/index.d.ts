/** One parsed snapshot of `docs/run-state.json`, reduced to what the band draws. */
export type Model = {
  domain: string
  /** The stage the run is in, 1 to 5. */
  stage: number
  /** Normalised status of stages 1 to 5. */
  stages: Status[]
  /** Normalised status by phase key ("0".."12", "smoke"). */
  phases: Record<string, Status>
  openDecisions: number
}

export type Status = 'done' | 'doing' | 'stale' | 'todo'

declare module 'claude-code' {
  interface PluginState {
    'wordpress-to-astro-progress': {
      /** Latest snapshot, or null when no run state has been read yet. */
      model: Model | null
      /** True once the skill was invoked in this session or a run state exists. */
      active: boolean
      isHidden: boolean
    }
  }
}
