# notion-search-alfred5-workflow
An Alfred 5 workflow to search Notion.so with instant results

![img](https://raw.githubusercontent.com/wrjlewis/notion-search-alfred5-workflow/main/Screenshot.png)

**Alfred 5 version (this one)**

[Github Repository](https://github.com/wrjlewis/notion-search-alfred5-workflow)

[Latest Download](https://github.com/wrjlewis/notion-search-alfred5-workflow/releases/latest/download/Notion.Search.Alfred.5.alfredworkflow)

**Alfred 4 version**

[Github Repository](https://github.com/wrjlewis/notion-search-alfred-workflow)

[Latest Download](https://github.com/wrjlewis/notion-search-alfred-workflow/releases/latest/download/Notion.Search.alfredworkflow)

Simply type your keyword into Alfred (default: ns) and provide a query to see instant search results from Notion that mimic the Quick Find function in the Notion webapp. Selecting a search result takes you to that page in Notion in your default web browser or notion app.

Comes with pre-configured support for [OneUpdater](https://github.com/vitorgalvao/alfred-workflows/tree/master/OneUpdater) for automatic version updates.

The workflow also provides the ability to quickly see your __recently viewed pages__. Simply type the 'ns' keyword to start the workflow, as you would before you search, and your most recently viewed notion pages are displayed. There is and environment variable to toggle this feature if you'd like to turn this off (detailed below).

![img](https://raw.githubusercontent.com/wrjlewis/notion-search-alfred5-workflow/main/alfred%20notion%20search.gif)

## User Configuration

- `Cookie`: Needed for your Notion token. 
- `Space ID`: Your organisation identifier.
- `Navigable Only`: Defaults to False. Setting to false allows you to search objects within a page, ie notion objects that cannot be found through the left hand side navigation pane.
- `Use Desktop Client`: Defaults to False. Determines whether to open Notion links in the desktop client rather than the web app.
- `Enable Icons`: Defaults to True. This toggles support for Notion icons to be shown natively in Alfred search results, for a better design/UX experience. Custom Notion icons are downloaded on demand and cached.
- `Show Recently Viewed`: Defaults to True. This toggle determines if recently viewed pages should be shown when there is no query provided by the user and the user id is present in the supplied cookie (user id is needed for the api call to show recently viewed pages).
- `Icon Cache Days`: Defaults to the recommended value of 365 days for the best performance. Defines the number of days to cache icons and images. Min 0, max 365.

## Install Steps

### Install cairosvg (optional)

Install cairosvg which will allow svg icons to be shown in Alfred search results. Open terminal and run the following command:

`pip3 install cairosvg`

Install cairosvgs's dependency, cairo. With [Homebrew](https://brew.sh/) for example:

`brew install cairo`

### Get your workflow variables

I recommend using chrome to retrieve these values. If you can only use safari you can copy the 'token_v2' value by following the equivalent steps above and populating the cookie env variable in Alfred so it looks like this `token_v2=XXXXXXXXXXXX`.

Visit the Notion webapp and use your browser developer tools to see the network requests being made when you type in anything to the quick find search bar.

Here you'll see a request called `search`, check the request headers to copy the `cookie` value and check the request payload to copy your `notionSpaceId`.

Known issue: Some users have experienced issues with copying these values directly from developer tools, but have seen success by copying and pasting the values into TextEdit or a different text editor first, this probably "strips out" or removes any problematic formatting.

[![img](https://i.imgur.com/ytewFzE.gif)](https://i.imgur.com/ytewFzE.gif)


__Get your `cookie` headers__
They should look something like this 

```
notion_browser_id=1bcfbfb9-e98c-9f03; logglytrbckingsession=eb1c82cb-fd; bjs_bnonymous_id=%22bdbf1088-b33c-9bdb-b67c-1e; _fbp=fb.1.12821; intercom-id-gpfdrxfd=b61ec62d-; token_v2=b39099...

```

[![img](https://github.com/wrjlewis/notion-search-alfred-workflow/blob/master/cookie.png)](https://github.com/wrjlewis/notion-search-alfred-workflow/blob/master/spaceId.png)


__Get your `spaceId`__
It should look something like this

```
celcl9aa-c3l7-7504-ca19-0c985e34ll8d
```

[![img](https://github.com/wrjlewis/notion-search-alfred-workflow/blob/master/spaceId.png)](https://github.com/wrjlewis/notion-search-alfred-workflow/blob/master/spaceId.png)

### Install the Notion Alfred worflow

Download and double click the [latest release](https://github.com/wrjlewis/notion-search-alfred5-workflow/releases/latest/download/Notion.Search.Alfred.5.alfredworkflow). Follow the steps shown in Alfred to install the workflow.

### Add these values to the Notion Alfred workflow

Alfred should automatically open the 'configure workflow' options panel when you first install the workflow, here you can add the values obtained through the above steps. 

You can also update these values at any time by clicking Configure Workflow..

[![img](https://raw.githubusercontent.com/wrjlewis/notion-search-alfred5-workflow/main/configure.png)](https://raw.githubusercontent.com/wrjlewis/notion-search-alfred5-workflow/main/configure.png)

## Troubleshooting

The script may fail due to an SSL error.  If the script isn't working, turn on debugging by clicking on the little cockroach in the alfred workflow screen.  If you see an error like:

``` [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: ..... ```

Run this from the terminal app:

``` '/Applications/Python 3.9/Install Certificates.command' ```

The single quotes are required.
If this file doesn't exist, run "python --version" to find out what version you have
and update the directory accordingly.

## Tips

- If you prefer using the Mac app rather than using Notion in your browser, check `Use Desktop Client` under the menu that appears when you click 'Configure Workflow..' as shown above in the [install steps](https://github.com/wrjlewis/notion-search-alfred5-workflow#add-these-values-to-the-notion-alfred-workflow) section.

## Download:
https://github.com/wrjlewis/notion-search-alfred5-workflow/releases/latest/download/Notion.Search.Alfred.5.alfredworkflow

## Forum topics:
https://www.alfredforum.com/topic/14451-notionso-instant-search-workflow/
https://www.reddit.com/r/NotionSo/comments/f58u1y/notionso_instant_search_workflow_for_alfred/
