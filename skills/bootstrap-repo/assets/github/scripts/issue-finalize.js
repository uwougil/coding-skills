'use strict';

const REFS_LINE = /^\s*Refs\s+#([1-9]\d*)\s*$/gim;

function parseIssueReferences(body) {
  const issueNumbers = new Set();
  const text = typeof body === 'string' ? body : '';
  let match;
  while ((match = REFS_LINE.exec(text)) !== null) {
    issueNumbers.add(Number(match[1]));
  }
  REFS_LINE.lastIndex = 0;
  return [...issueNumbers];
}

function commentMarker(run, issueNumber, outcome) {
  const attempt = run.run_attempt || 1;
  return `<!-- main-ci-issue-finalize run:${run.id} attempt:${attempt} issue:${issueNumber} outcome:${outcome} -->`;
}

const DEFAULT_MESSAGES = {
  success: ({ prNumber }) => `Main CI passed for PR #${prNumber}. Closing this Issue as completed.`,
  failure: ({ prNumber, conclusion }) => `Main CI failed to reach success after PR #${prNumber} was merged (conclusion: \`${conclusion}\`). This Issue remains open and requires follow-up.`,
};

function commentBody(run, prNumber, issueNumber, outcome, messages = DEFAULT_MESSAGES) {
  const marker = commentMarker(run, issueNumber, outcome);
  const runLink = run.html_url ? `\nWorkflow run: ${run.html_url}` : '';
  const commit = run.head_sha ? `\nCommit: \`${run.head_sha}\`` : '';
  const conclusion = run.conclusion || 'unknown';
  const formatter = messages[outcome] || DEFAULT_MESSAGES[outcome];
  const message = formatter({ prNumber, issueNumber, conclusion, run });
  return `${marker}\n${message}${runLink}${commit}`;
}

async function finalize({ github, context, messages = DEFAULT_MESSAGES }) {
  const run = context.payload && context.payload.workflow_run;
  const repository = context.payload && context.payload.repository;
  const defaultBranch = repository && repository.default_branch;
  const summary = {
    pullRequests: 0,
    referencedIssues: 0,
    commentsCreated: 0,
    issuesClosed: 0,
    skipped: [],
  };

  if (!run || run.event !== 'push' || !defaultBranch || run.head_branch !== defaultBranch) {
    summary.skipped.push('not-default-branch-push-ci');
    return summary;
  }

  const owner = context.repo.owner;
  const repo = context.repo.repo;
  const associated = await github.paginate(github.rest.repos.listPullRequestsAssociatedWithCommit, {
    owner,
    repo,
    commit_sha: run.head_sha,
    per_page: 100,
  });
  const candidates = associated.filter((pr) =>
    Boolean(pr.merged_at) &&
    pr.base && pr.base.ref === defaultBranch &&
    pr.merge_commit_sha === run.head_sha
  );

  if (candidates.length === 0) {
    summary.skipped.push('no-merged-pr-for-main-ci-commit');
    return summary;
  }

  const outcome = run.conclusion === 'success' ? 'success' : 'failure';
  const errors = [];

  for (const candidate of candidates) {
    try {
      const response = await github.rest.pulls.get({ owner, repo, pull_number: candidate.number });
      const pr = response.data;
      if (!pr.merged_at || !pr.base || pr.base.ref !== defaultBranch || pr.merge_commit_sha !== run.head_sha) {
        summary.skipped.push(`pr-${candidate.number}-not-exact-merge`);
        continue;
      }
      summary.pullRequests += 1;
      const issueNumbers = parseIssueReferences(pr.body);
      if (issueNumbers.length === 0) {
        summary.skipped.push(`pr-${pr.number}-has-no-refs`);
        continue;
      }

      for (const issueNumber of issueNumbers) {
        summary.referencedIssues += 1;
        try {
          const issueResponse = await github.rest.issues.get({ owner, repo, issue_number: issueNumber });
          const issue = issueResponse.data;
          if (issue.pull_request) {
            summary.skipped.push(`#${issueNumber}-is-a-pull-request`);
            continue;
          }
          if (issue.state !== 'open') {
            summary.skipped.push(`#${issueNumber}-already-closed`);
            continue;
          }

          const marker = commentMarker(run, issueNumber, outcome);
          const comments = await github.paginate(github.rest.issues.listComments, {
            owner,
            repo,
            issue_number: issueNumber,
            per_page: 100,
          });
          if (!comments.some((comment) => typeof comment.body === 'string' && comment.body.includes(marker))) {
            await github.rest.issues.createComment({
              owner,
              repo,
              issue_number: issueNumber,
              body: commentBody(run, pr.number, issueNumber, outcome, messages),
            });
            summary.commentsCreated += 1;
          }

          if (outcome === 'success') {
            await github.rest.issues.update({
              owner,
              repo,
              issue_number: issueNumber,
              state: 'closed',
              state_reason: 'completed',
            });
            summary.issuesClosed += 1;
          }
        } catch (error) {
          errors.push(`Issue #${issueNumber}: ${error.message}`);
        }
      }
    } catch (error) {
      errors.push(`PR #${candidate.number}: ${error.message}`);
    }
  }

  if (errors.length > 0) {
    throw new Error(`Issue finalization completed with errors:\n${errors.join('\n')}`);
  }
  return summary;
}

module.exports = finalize;
module.exports.parseIssueReferences = parseIssueReferences;
module.exports.commentMarker = commentMarker;
module.exports.commentBody = commentBody;
module.exports.DEFAULT_MESSAGES = DEFAULT_MESSAGES;
