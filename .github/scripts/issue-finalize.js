'use strict';

const finalize = require('../../skills/bootstrap-repo/assets/github/scripts/issue-finalize.js');

module.exports = ({ github, context }) => finalize({
  github,
  context,
  messages: {
    success: ({ prNumber }) => `PR #${prNumber} 的 Main CI 已通过。自动将此 Issue 标记为完成并关闭。`,
    failure: ({ prNumber, conclusion }) => `PR #${prNumber} 合并后的 Main CI 未成功（结论：\`${conclusion}\`）。此 Issue 保持 Open，需要继续处理。`,
  },
});
