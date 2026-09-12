"""Insert verified profile links into README.md without inventing user data."""

from html import escape
from pathlib import Path
from urllib.parse import quote


README = Path(__file__).with_name("README.md")


def replace_section(text: str, name: str, content: str) -> str:
    start = f"<!-- {name}_START -->"
    end = f"<!-- {name}_END -->"
    before, separator, remainder = text.partition(start)
    if not separator:
        raise ValueError(f"Missing marker: {start}")
    _, separator, after = remainder.partition(end)
    if not separator:
        raise ValueError(f"Missing marker: {end}")
    return f"{before}{start}\n{content}\n{end}{after}"


def badge(label: str, action: str, color: str, destination: str) -> str:
    image = f"https://img.shields.io/badge/{label}-{action}-{color}?style=for-the-badge"
    return f"[![{label.title()}]({image})]({destination})"


def main() -> None:
    username = input("GitHub username [iammoussaab]: ").strip() or "iammoussaab"
    email = input("Public email [mossabelmahraoui@gmail.com]: ").strip() or "mossabelmahraoui@gmail.com"
    linkedin = input("LinkedIn URL (optional): ").strip()
    portfolio = input("Portfolio URL [ArtStation]: ").strip() or "https://www.artstation.com/moussaabelmahraoui5"
    itch = input("Itch.io URL (optional): ").strip()

    safe_username = quote(username, safe="-")
    links = [badge("GITHUB", "PROFILE", "181717", f"https://github.com/{safe_username}")]
    if portfolio:
        links.append(badge("PORTFOLIO", "ENTER", "111827", escape(portfolio, quote=True)))
    if linkedin:
        links.append(badge("LINKEDIN", "CONNECT", "0A66C2", escape(linkedin, quote=True)))
    if email:
        links.append(badge("EMAIL", "SEND", "7C3AED", f"mailto:{quote(email, safe='@.+-')}"))
    if itch:
        links.append(badge("ITCH.IO", "PLAY", "FA5C5C", escape(itch, quote=True)))

    links_content = "\n".join(links) or "<!-- No public contact links configured. -->"

    if username:
        snake_content = f'''<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/{safe_username}/{safe_username}/output/github-snake-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/{safe_username}/{safe_username}/output/github-snake.svg">
    <img alt="Animated snake moving across Moussaab's GitHub contribution calendar" src="https://raw.githubusercontent.com/{safe_username}/{safe_username}/output/github-snake.svg">
  </picture>
</p>'''
    else:
        snake_content = "The contribution snake requires a GitHub username. Run this script again after one is available."

    text = README.read_text(encoding="utf-8")
    text = replace_section(text, "PROFILE_LINKS", links_content)
    text = replace_section(text, "CONTRIBUTION_SNAKE", snake_content)
    README.write_text(text, encoding="utf-8")
    print("README.md updated with the verified values provided.")


if __name__ == "__main__":
    main()
