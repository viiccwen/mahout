#!/usr/bin/env node
//
// Licensed to the Apache Software Foundation (ASF) under one or more
// contributor license agreements.  See the NOTICE file distributed with
// this work for additional information regarding copyright ownership.
// The ASF licenses this file to You under the Apache License, Version 2.0.
//
// Usage: node scripts/set-docs-version.js 0.7
// Sets versions.current.label to VERSION and syncs config versions with versions.json
// so only existing versioned docs are listed (avoids "unknown versions" errors).
const fs = require('fs');
const path = require('path');

const version = process.argv[2];
if (!version || !/^\d+\.\d+(\.\d+)?$/.test(version)) {
  console.error('Usage: node scripts/set-docs-version.js <VERSION> (e.g. 0.7 or 1.2.3)');
  process.exit(1);
}

const websiteDir = path.join(__dirname, '..');
const configPath = path.join(websiteDir, 'docusaurus.config.ts');
const versionsPath = path.join(websiteDir, 'versions.json');

let content = fs.readFileSync(configPath, 'utf8');

// 1. Set current.label to VERSION
content = content.replace(
  /(current:\s*\{\s*label:\s*)'[^']+'/,
  (_, prefix) => `${prefix}'${version}'`
);

// 2. Replace the whole versions object with current + only versions from versions.json
let existingVersions = [];
try {
  existingVersions = JSON.parse(fs.readFileSync(versionsPath, 'utf8'));
} catch (_) {
  // no versions.json or invalid; config will have current only
}

const versionEntries = existingVersions
  .map((v) => `            '${v}': {
              label: '${v}',
              path: '${v}',
            }`)
  .join(',\n');

const newVersionsBlock = `versions: {
            current: {
              label: '${version}',
              path: '',
            }${versionEntries ? ',\n' + versionEntries : ''}
          }`;

content = content.replace(
  /versions:\s*\{[\s\S]*?^          \},\s*\n\s*\},/m,
  newVersionsBlock + ',\n        },'
);

fs.writeFileSync(configPath, content);
console.log(`Updated docusaurus.config.ts: current label '${version}', versions synced with versions.json.`);
