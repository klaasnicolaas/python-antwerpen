<!-- Banner -->
![alt Banner of the odp antwerpen package](https://raw.githubusercontent.com/klaasnicolaas/python-antwerpen/main/assets/header_odp_antwerpen-min.png)

<!-- PROJECT SHIELDS -->
[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits-url]
[![PyPi Downloads][downloads-shield]][downloads-url]
[![GitHub Last Commit][last-commit-shield]][commits-url]
[![Open in Dev Containers][devcontainer-shield]][devcontainer]

[![Code Quality][code-quality-shield]][code-quality]
[![Build Status][build-shield]][build-url]
[![Typing Status][typing-shield]][typing-url]

[![Maintainability][maintainability-shield]][maintainability-url]
[![Code Coverage][codecov-shield]][codecov-url]

Asynchronous Python client for the open datasets of Antwerpen (Belgium).

## About

A python package with which you can retrieve data from the Open Data Platform of Antwerpen via [their API][api]. This package was initially created to only retrieve parking data from the API, but the code base is made in such a way that it is easy to extend for other datasets from the same platform.

## Installation

```bash
pip install antwerpen
```

## Datasets

You can read the following datasets with this package:

- [Disabled parking spaces / Parkeerplaatsen voor personen met een handicap][disabled_parkings] (1666 locations)

---

There are a number of parameters you can set to retrieve the data:

- **limit** (default: 10) - How many results you want to retrieve.

<details>
    <summary>Click here to get more details</summary>

### Disabled parking spaces

| Variable | Type | Description |
| :------- | :--- | :---------- |
| `entry_id` | integer | The ID of this location |
| `number` | integer | The number of parking spots on this location |
| `orientation` | string | The orientation of this location |
| `destination` | string | The destination of this location |
| `window_time` | string (none) | The window time of this location |
| `lined` | boolean | Whether this location is lined |
| `status` | string | The status of this location |
| `gis_id` | string | The GIS ID of this location |
| `created_at` | datetime | The date this location was added to the dataset, not all locations have a value |
| `coordinates` | list (float) | The coordinates of this location |

</details>

## Example

```python
import asyncio

from antwerpen import ODPAntwerpen


async def main() -> None:
    """Show example on using the Parking Antwerpen API client."""
    async with ODPAntwerpen() as client:
        disabled_parkings = await client.disabled_parkings(limit=10)
        print(disabled_parkings)


if __name__ == "__main__":
    asyncio.run(main())
```

## Use cases

[NIPKaart.nl][nipkaart]

A website that provides insight into where disabled parking spaces are, based on data from users and municipalities. Operates mainly in the Netherlands, but also has plans to process data from abroad.

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We've set up a separate document for our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

The simplest way to begin is by utilizing the [Dev Container][devcontainer]
feature of Visual Studio Code or by opening a CodeSpace directly on GitHub.
By clicking the button below you immediately start a Dev Container in Visual Studio Code.

[![Open in Dev Containers][devcontainer-shield]][devcontainer]

This Python project relies on [Poetry][poetry] as its dependency manager,
providing comprehensive management and control over project dependencies.

You need at least:

- Python 3.9+
- [Poetry][poetry-install]

Install all packages, including all development requirements:

```bash
poetry install
```

Poetry creates by default an virtual environment where it installs all
necessary pip packages, to enter or exit the venv run the following commands:

```bash
poetry shell
exit
```

Setup the pre-commit check, you must run this inside the virtual environment:

```bash
pre-commit install
```

*Now you're all set to get started!*

As this repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
poetry run pre-commit run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```

## Credits

Photo used in header was taken by [Bert Kaufmann](https://www.flickr.com/photos/22746515@N02/50497311187/in/photostream/).

## License

MIT License

Copyright (c) 2022-2023 Klaas Schoute

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[api]: https://portaal-stadantwerpen.opendata.arcgis.com
[disabled_parkings]: https://portaal-stadantwerpen.opendata.arcgis.com/datasets/stadAntwerpen::parkeerplaatsen-voor-personen-met-een-handicap/about
[nipkaart]: https://www.nipkaart.nl

<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://github.com/klaasnicolaas/python-antwerpen/actions/workflows/tests.yaml/badge.svg
[build-url]: https://github.com/klaasnicolaas/python-antwerpen/actions/workflows/tests.yaml
[code-quality-shield]: https://github.com/klaasnicolaas/python-antwerpen/actions/workflows/codeql.yaml/badge.svg
[code-quality]: https://github.com/klaasnicolaas/python-antwerpen/actions/workflows/codeql.yaml
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-antwerpen.svg
[commits-url]: https://github.com/klaasnicolaas/python-antwerpen/commits/main
[codecov-shield]: https://codecov.io/gh/klaasnicolaas/python-antwerpen/branch/main/graph/badge.svg?token=LJULYJC8VT
[codecov-url]: https://codecov.io/gh/klaasnicolaas/python-antwerpen
[devcontainer-shield]: https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode
[devcontainer]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/klaasnicolaas/python-antwerpen
[downloads-shield]: https://img.shields.io/pypi/dm/antwerpen
[downloads-url]: https://pypistats.org/packages/antwerpen
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-antwerpen.svg
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-antwerpen.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2023.svg
[maintainability-shield]: https://api.codeclimate.com/v1/badges/43af030f43d5f3bc6a90/maintainability
[maintainability-url]: https://codeclimate.com/github/klaasnicolaas/python-antwerpen/maintainability
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[pypi]: https://pypi.org/project/antwerpen/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/antwerpen
[typing-shield]: https://github.com/klaasnicolaas/python-antwerpen/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/klaasnicolaas/python-antwerpen/actions/workflows/typing.yaml
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-antwerpen.svg
[releases]: https://github.com/klaasnicolaas/python-antwerpen/releases

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com
