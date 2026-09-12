# Setup — Moussaab Game Profile

This folder is ready to become a GitHub profile README.

## 1. Create the profile repository

The repository must be public and its name must exactly match your GitHub username. For example, the username `moussaabdev` requires the repository `moussaabdev/moussaabdev`.

## 2. Add verified links

Run:

```bash
python setup_profile.py
```

The script asks for your GitHub username and optional public email, LinkedIn, portfolio, and itch.io URLs. Blank optional fields are omitted. Review the generated links before publishing; the script does not verify ownership or availability.

You still need to provide:

- GitHub username
- Public email, if desired
- LinkedIn URL, if available
- Portfolio URL, if available
- itch.io URL, if available
- Repository, demo, video, or media links for each featured project

## 3. Publish

Copy `README.md`, `assets/`, and `.github/` into the profile repository, then commit and push them to its default branch.

## 4. Enable the contribution snake

In the repository's **Actions** tab, run **Generate contribution snake** once. The workflow creates an `output` branch and then runs daily. If it cannot push, check **Settings → Actions → General → Workflow permissions** and allow read and write permissions.

The snake URLs are only inserted when a GitHub username is supplied to the setup script. The README remains valid if this optional feature is not configured.

## 5. Recommended pinned-repository order

Choose the strongest public, documented repositories available:

1. Sheep with Guns
2. Lost in Sala Colonia or the strongest VR/XR project
3. ZAMZAMAN or the strongest additional Unity project
4. Kasbah
5. SAQR
6. Hospital Anomaly, a reusable tool, or another polished game

Prefer repositories with a clear README, screenshots or video, setup instructions, and an honest statement of your contribution. Do not pin tutorial-only or inaccessible projects when stronger work is available.
