'use strict';

const assert = require('node:assert/strict');
const finalize = require('../assets/github/scripts/issue-finalize.js');
const localizedFinalize = require('../../../.github/scripts/issue-finalize.js');

function mergedPr(number, body, sha = 'abc123') {
  return {
    number,
    body,
    merged_at: '2026-09-07T00:00:00Z',
    merge_commit_sha: sha,
    base: { ref: 'main' },
  };
}

function contextFor(overrides = {}) {
  return {
    repo: { owner: 'octo', repo: 'example' },
    payload: {
      repository: { default_branch: 'main' },
      workflow_run: {
        id: 77,
        run_attempt: 1,
        event: 'push',
        head_branch: 'main',
        head_sha: 'abc123',
        conclusion: 'success',
        html_url: 'https://github.com/octo/example/actions/runs/77',
        ...overrides,
      },
    },
  };
}

function mockGitHub({ prs = [], issues = {}, comments = {} } = {}) {
  const calls = { associated: 0, pulls: [], getIssue: [], listComments: [], createComment: [], update: [] };
  const github = {
    rest: {
      repos: {
        listPullRequestsAssociatedWithCommit: async () => {
          calls.associated += 1;
          return { data: prs };
        },
      },
      pulls: {
        get: async ({ pull_number }) => {
          calls.pulls.push(pull_number);
          return { data: prs.find((pr) => pr.number === pull_number) };
        },
      },
      issues: {
        get: async ({ issue_number }) => {
          calls.getIssue.push(issue_number);
          return { data: issues[issue_number] || { number: issue_number, state: 'open' } };
        },
        listComments: async ({ issue_number }) => {
          calls.listComments.push(issue_number);
          return { data: comments[issue_number] || [] };
        },
        createComment: async (params) => {
          calls.createComment.push(params);
          return { data: {} };
        },
        update: async (params) => {
          calls.update.push(params);
          return { data: {} };
        },
      },
    },
  };
  github.paginate = async (method, params) => (await method(params)).data;
  return { github, calls };
}

async function test(name, fn) {
  try {
    await fn();
    process.stdout.write(`ok - ${name}\n`);
  } catch (error) {
    process.stderr.write(`not ok - ${name}\n${error.stack}\n`);
    process.exitCode = 1;
  }
}

async function run() {
  await test('success comments and closes an open real Issue', async () => {
    const { github, calls } = mockGitHub({ prs: [mergedPr(42, 'Refs #123')] });
    const result = await finalize({ github, context: contextFor() });
    assert.equal(result.commentsCreated, 1);
    assert.equal(result.issuesClosed, 1);
    assert.match(calls.createComment[0].body, /Main CI passed for PR #42/);
    assert.equal(calls.update[0].issue_number, 123);
    assert.equal(calls.update[0].state, 'closed');
    assert.equal(calls.update[0].state_reason, 'completed');
  });

  await test('repository wrapper localizes human-facing comments', async () => {
    const { github, calls } = mockGitHub({ prs: [mergedPr(42, 'Refs #123')] });
    await localizedFinalize({ github, context: contextFor() });
    assert.match(calls.createComment[0].body, /Main CI 已通过/);
    assert.match(calls.createComment[0].body, /PR #42/);
  });

  await test('every non-success conclusion comments and keeps the Issue open', async () => {
    for (const conclusion of [
      'failure',
      'cancelled',
      'timed_out',
      'action_required',
      'stale',
      'neutral',
      'skipped',
      'unexpected_future_conclusion',
    ]) {
      const { github, calls } = mockGitHub({ prs: [mergedPr(42, 'Refs #123')] });
      const result = await finalize({ github, context: contextFor({ conclusion }) });
      assert.equal(result.commentsCreated, 1);
      assert.equal(result.issuesClosed, 0);
      assert.equal(calls.update.length, 0);
      assert.match(calls.createComment[0].body, /Main CI failed to reach success/);
      assert.match(calls.createComment[0].body, /remains open/);
      assert.match(calls.createComment[0].body, new RegExp(conclusion));
    }
  });

  await test('finalization never exposes an Issue deletion path', async () => {
    const { github } = mockGitHub({ prs: [mergedPr(42, 'Refs #123')] });
    assert.equal(github.rest.issues.delete, undefined);
    assert.equal(github.rest.issues.deleteIssue, undefined);
    await finalize({ github, context: contextFor() });
  });

  await test('PR CI never looks up or closes Issues', async () => {
    const { github, calls } = mockGitHub({ prs: [mergedPr(42, 'Refs #123')] });
    const result = await finalize({ github, context: contextFor({ event: 'pull_request', head_branch: 'feature' }) });
    assert.deepEqual(result.skipped, ['not-default-branch-push-ci']);
    assert.equal(calls.associated, 0);
    assert.equal(calls.update.length, 0);
  });

  await test('a direct main push without an associated merged PR exits safely', async () => {
    const { github, calls } = mockGitHub();
    const result = await finalize({ github, context: contextFor() });
    assert.deepEqual(result.skipped, ['no-merged-pr-for-main-ci-commit']);
    assert.equal(calls.getIssue.length, 0);
  });

  await test('a merged PR without exact Refs lines exits safely', async () => {
    const { github, calls } = mockGitHub({ prs: [mergedPr(42, 'Related discussion #123')] });
    const result = await finalize({ github, context: contextFor() });
    assert.deepEqual(result.skipped, ['pr-42-has-no-refs']);
    assert.equal(calls.getIssue.length, 0);
  });

  await test('an already closed Issue is not commented on or closed again', async () => {
    const { github, calls } = mockGitHub({
      prs: [mergedPr(42, 'Refs #123')],
      issues: { 123: { number: 123, state: 'closed' } },
    });
    const result = await finalize({ github, context: contextFor() });
    assert.deepEqual(result.skipped, ['#123-already-closed']);
    assert.equal(calls.createComment.length, 0);
    assert.equal(calls.update.length, 0);
  });

  await test('the same failed workflow attempt does not create duplicate comments', async () => {
    const run = contextFor({ conclusion: 'failure' }).payload.workflow_run;
    const marker = finalize.commentMarker(run, 123, 'failure');
    const { github, calls } = mockGitHub({
      prs: [mergedPr(42, 'Refs #123')],
      comments: { 123: [{ body: `${marker}\nalready reported` }] },
    });
    const result = await finalize({ github, context: contextFor({ conclusion: 'failure' }) });
    assert.equal(result.commentsCreated, 0);
    assert.equal(calls.createComment.length, 0);
    assert.equal(calls.update.length, 0);
  });

  await test('a later successful rerun has a distinct marker and closes the Issue', async () => {
    const failedRun = contextFor({ conclusion: 'failure', run_attempt: 1 }).payload.workflow_run;
    const oldMarker = finalize.commentMarker(failedRun, 123, 'failure');
    const { github, calls } = mockGitHub({
      prs: [mergedPr(42, 'Refs #123')],
      comments: { 123: [{ body: `${oldMarker}\nfailed attempt` }] },
    });
    const result = await finalize({ github, context: contextFor({ conclusion: 'success', run_attempt: 2 }) });
    assert.equal(result.commentsCreated, 1);
    assert.equal(result.issuesClosed, 1);
    assert.match(calls.createComment[0].body, /attempt:2/);
  });

  await test('multiple exact Refs lines finalize multiple Issues', async () => {
    const { github, calls } = mockGitHub({ prs: [mergedPr(42, 'Refs #123\nRefs #456\nRefs #123')] });
    const result = await finalize({ github, context: contextFor() });
    assert.equal(result.referencedIssues, 2);
    assert.deepEqual(calls.update.map((call) => call.issue_number), [123, 456]);
  });

  await test('a referenced Pull Request is never treated as an Issue', async () => {
    const { github, calls } = mockGitHub({
      prs: [mergedPr(42, 'Refs #123')],
      issues: { 123: { number: 123, state: 'open', pull_request: { url: 'api/pr/123' } } },
    });
    const result = await finalize({ github, context: contextFor() });
    assert.deepEqual(result.skipped, ['#123-is-a-pull-request']);
    assert.equal(calls.createComment.length, 0);
    assert.equal(calls.update.length, 0);
  });

  await test('reference parsing is strict and deduplicated', async () => {
    assert.deepEqual(
      finalize.parseIssueReferences('See #1\nRefs #12 text\nRefs #0\nRefs #23\n refs #23 \nRefs #45'),
      [23, 45],
    );
  });
}

run();
