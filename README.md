# Built with Hydra Engine

Projects made by reverse-engineering programs their authors own, with
[Hydra Engine](https://github.com/RusticStack/hydra-engine) and
[Hydralysis](https://github.com/RusticStack/Hydralysis). The
[showcase on the website](https://www.hydrare.dev/examples) reads this repository's
`index.json`, so a project merged here appears there.

## Add yours

**By pull request.** Make a folder `projects/<your-project>/` (lowercase words joined by `-`) with:

- `project.json`, following [`project.schema.json`](project.schema.json):

  ```json
  {
    "name": "My Project",
    "url": "https://github.com/you/my-project",
    "from": "what you reverse-engineered",
    "to": "what it became",
    "kind": "game",
    "text": "One or two sentences, in your words, shown on the card.",
    "author": "you",
    "stack": ["Claude Code", "Hydralysis"],
    "highlights": ["a measured fact", "another"],
    "added": "2026-10-27"
  }
  ```

  `kind` is one of `game`, `tool`, `driver`, `firmware`, `mod`, `research`; `authorUrl` and
  `highlights` (up to three) are optional.
- one cover image, `cover.jpg`, `cover.png` or `cover.webp`: 1200x630, at most 600 KB.

Then run `python scripts/build_index.py` (Python 3, standard library only) and commit the updated
`index.json`. CI runs `python scripts/build_index.py --check` on every pull request.

**By issue.** Open an [Add a project](../../issues/new?template=project.yml) issue, attach the
cover, and a maintainer adds it.

## Rules

- Only programs you own, and no code, assets or data from them in your project.
- A link people can open: a repository, a release, a write-up or a video.
- A cover you have the right to share. Covers and descriptions belong to their authors, who
  license them for display on this showcase and the Hydra Engine website. Fan projects use their
  subject's name to say what they are, not to claim any affiliation.

The scripts and schema here are MIT-licensed ([LICENSE](LICENSE)).
