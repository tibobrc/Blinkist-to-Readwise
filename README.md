# Blinkist2Readwise

Blinkist2Readwise is a script to extract highlights from your Blinkist account and upload them to your Readwise account.  
You also have the option to extract your Blinkist highlights to a CSV file.

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [How the script works](#how-the-script-works)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

1. Have a Blinkist account, to which you log in **using email and password**.  
   Other methods of connection (e.g. with Google) are not currently supported by the script.
2. (Optional) Get the token required to access your Readwise account, if you wish to upload Blinkist highlights to Readwise.  
   You can find this token [here](https://readwise.io/access_token).
3. Have Python version >= 3.7 installed on your system.
4. Have Chrome installed on your system.
5. Have a ChromeDriver added to your system’s PATH (required to run `selenium`). Please refer to [this wiki](https://github.com/tibobrc/Blinkist2Readwise/wiki/Setting-Up-ChromeDriver) for downloading and setting up ChromeDriver.

### Setup & Installation
 
1. Clone this repository.
    ```sh
    git clone https://github.com/tibobrc/Blinkist2Readwise.git
    ```
2. Navigate to the directory and install the pre-requisite packages:
   * Using pip:
     ```sh
     pip install -r requirements.txt
     ```
   * Using conda:
     ```sh
     conda install --file requirements.txt
     ```

## Usage

```
blinkist2readwise.py [-h] [-d] [-s] [-t TOKEN_READWISE] blinkist_email blinkist_password
```

Required positional arguments:
* `blinkist_email`: the email address used to log in to your Blinkist account
* `blinkist_password`: the password used to log in to your Blinkist account

Optional arguments:
* `-h`, `--help`: show the help message and exit
* `-d`, `--download`: download all Blinkist highlights into a CSV file.
* `-s`, `--show-chrome`: show the Chrome window while extracting Blinkist highlights
* `-t TOKEN_READWISE`, `--token-readwise TOKEN_READWISE`: specify the token used to access your Readwise highlights.

**Note**: If you run the script without specifying a Readwise token, then the script will automatically download all your Blinkist highlights into a CSV. In that case, the option `-d` is redundant.

### Example

If you wish to upload your Blinkist highlights to Readwise without downloading the CSV file and without seeing the generated Chrome window, navigate into the directory you cloned and run
   ```sh
   python blinkist2readwise.py -t your_readwise_token your_blinkist_email your_blinkist_password
   ```
, replacing `your_readwise_token`, `your_blinkist_email` and `your_blinkist_password` with your actual credentials.

## How the script works

When executed, the script follows these steps:  

1. If the user chose to upload the Blinkist highlights to Readwise (option `-t`) and not to download all Blinkist highlights into a CSV (i.e. not the option `-d`), use the `requests` package and the token passed when calling the script to fetch the user's current Readwise highlights from the Readwise API.  
These Readwise highlights will later be used to only load Blinkist highlights which are not already saved in the user's Readwise account.
2. Use the `selenium` package to navigate to the [highlights page](https://www.blinkist.com/en/nc/login?last_page_before_login=%2Fen%2Fnc%2Fhighlights) on the Blinkist website, and:
   * Allow cookies, if prompted to.
   * Enter the user's Blinkist credentials which were passed when calling the script.
   * Click on the login button.
   * Order the highlights by date (if login successful).
3. If the user chose to upload the Blinkist highlights to Readwise and not to download all Blinkist highlights into a CSV:
   * Use the `beautifulsoup4` and `lxml` packages to extract the highlights information currently visible on the webpage.
   * Check if the oldest Blinkist highlight currently visible on the webpage is already saved in Readwise. If not, use the `selenium` package to click on the "Load More" button and repeat step 3.
4. If the user chose to save all the Blinkist highlights into a CSV, or did not specify a Readwise token, then use the `selenium` package to keep clicking on the "Load More" button as long as there are more highlights to load.
5. Use the `beautifulsoup4` and `lxml` packages to extract the highlights from the Blinkist webpage.
6. Use the `requests` package and the Readwise token passed when calling the script to upload the highlights to Readwise through the Readwise API.

## Contributing

All contributions are very welcome!  
Please make sure to follow these guidelines:
- [Contribution guidelines](https://github.com/tibobrc/Blinkist2Readwise/blob/main/CONTRIBUTING.md)
- [Code of conduct guidelines](https://github.com/tibobrc/Blinkist2Readwise/blob/main/CODE_OF_CONDUCT.md)

## License

Distributed under the MIT License. See [LICENSE](https://github.com/tibobrc/Blinkist2Readwise/blob/main/LICENSE) for more information.