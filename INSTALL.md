# Installing the XXE add-on

## Prerequesits
- Python: install from [Python3](https://www.python.org/downloads/) (Mac) or
[Python install manager](https://apps.microsoft.com/detail/9nq7512cxl7t) (Windows)
- Turn off Quick Start cache in XMlmind.
`Options` → `Preferences` → `Advanced` → `Cached data`

## Mac

```sh
mkdir -p ~/Library/Application\ Support/XMLmind/XMLEditor11/addon
ln -s ~/PATH/TO/giella-dict-xxe ~/Library/Application\ Support/XMLmind/XMLEditor11/addon/giella-dict-xxe
```

For PDFs:
```sh
brew install weasyprint
```

## Linux

```sh
mkdir -p ~/.xxe11/addon
ln -s ~/PATH/TO/giella-dict-xxe ~/.xxe11/addon/giella-dict-xxe
```

For PDFs:
```sh
sudo apt install weasyprint
```

## Windows (Command Prompt):

```
setx XXE_ADDON_PATH "C:\Users\NAME\PATH\TO\giella-dict-xxe;+"
```

For PDFs:  
Fetch the latest WeasyPrint for Windows from
<https://github.com/Kozea/WeasyPrint/releases> (`weasyprint-windows-onefile.zip`
which is found under "Assets" under the latest release), extract the zip file and
move `weasyprint.exe` to a new folder named `tools` inside `giella-dict-xxe`.
