# Bug Issue

Normalize runs of whitespace in titles without changing the public function API. Formatter redesign and unrelated cleanup are out of scope.

Acceptance: a title containing three consecutive spaces is normalized to one space, existing behavior remains covered, and focused tests pass.
