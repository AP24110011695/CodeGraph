import type {
  CommitRecordDto,
  RepositoryTimelineDto,
  SnapshotComparison,
  TimelineSnapshot,
} from './timeline.types';

export function adaptCommitToSnapshot(commit: CommitRecordDto): TimelineSnapshot {
  return {
    id: commit.sha,
    sha: commit.sha,
    label: commit.sha.slice(0, 7),
    timestamp: commit.timestamp,
    author: commit.author,
    message: commit.message,
    filesChanged: commit.files_changed.length,
    insertions: commit.insertions,
    deletions: commit.deletions,
    modules: commit.modules_touched,
  };
}

export function adaptTimelineSnapshots(dto: RepositoryTimelineDto): TimelineSnapshot[] {
  return dto.commits.map(adaptCommitToSnapshot);
}

export function compareSnapshots(
  left: TimelineSnapshot,
  right: TimelineSnapshot,
  leftCommit?: CommitRecordDto,
  rightCommit?: CommitRecordDto
): SnapshotComparison {
  const leftFiles = new Set(leftCommit?.files_changed ?? []);
  const rightFiles = new Set(rightCommit?.files_changed ?? []);
  const addedFiles = [...rightFiles].filter((f) => !leftFiles.has(f));
  const removedFiles = [...leftFiles].filter((f) => !rightFiles.has(f));
  const sharedFiles = [...leftFiles].filter((f) => rightFiles.has(f));
  const leftModules = new Set(left.modules);
  const rightModules = new Set(right.modules);
  const moduleDelta = [
    ...[...rightModules].filter((m) => !leftModules.has(m)).map((m) => `+ ${m}`),
    ...[...leftModules].filter((m) => !rightModules.has(m)).map((m) => `- ${m}`),
  ];

  const changeSummary = [
    `${addedFiles.length} file(s) only in later commit`,
    `${removedFiles.length} file(s) only in earlier commit`,
    `${sharedFiles.length} overlapping file(s)`,
    `Net lines: +${right.insertions - left.insertions} / -${right.deletions - left.deletions}`,
  ].join('. ');

  return {
    left,
    right,
    addedFiles,
    removedFiles,
    sharedFiles,
    moduleDelta,
    changeSummary,
  };
}
