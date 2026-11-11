---
title: 'https://eugeneyan.com//writing/web-frameworks/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/web-frameworks/
account: 
origin: en-rss
---
# [eugeneyan](/)

* [Start Here](/start-here/ "Start Here")
* [Writing](/writing/ "Writing")
* [Speaking](/speaking/ "Speaking")
* [Prototyping](/prototyping/ "Prototyping")
* [About](/about/ "About")
* [![](/assets/icon-search.svg)](/search/ "Search")

# Building the Same App Using Various Web Frameworks

[
[learning](/tag/learning/)
[engineering](/tag/engineering/)
[python](/tag/python/)
[🛠](/tag/🛠/)
]
 · 8 min read

Recently, I’ve been wondering if I should migrate from my current web app stack (FastAPI, HTML, CSS, and a sprinkle of JavaScript) to a modern web framework. I was particularly interested in FastHTML, Next.js, and Svelte.

* **FastHTML**: [Many folks](https://x.com/search?q=fasthtml&src=typed_query) have started building with it since Jeremy Howard [launched](https://x.com/jeremyphoward/status/1818036923304456492) it a month ago. Its goal is to enable modern web applications in pure Python.
* **Next.js**: I’ve come across several apps built with it such as [cal.com](https://github.com/calcom/cal.com) and [roomGPT](https://github.com/Nutlope/roomGPT). It has a large ecosystem and is popular for building production-grade web apps.
* **SvelteKit**: This lightweight framework has been popular with devs ([Stack Overflow](https://survey.stackoverflow.co/2024/technology/#2-web-frameworks-and-technologies), [TSH](https://tsh.io/state-of-frontend/#which-of-the-following-frameworks-would-you-like-to-learn-in-the-future), [State of JS](https://2022.stateofjs.com/en-US/libraries/front-end-frameworks/)) and my friend Swyx ([Why I Enjoy Svelte](https://www.swyx.io/svelte-why)) over the past few years.

To learn more about these frameworks, I built the same web app using each of them. The app, which I’m calling “Look at Your Data”, allows users to:

* `Upload` a CSV file to initialize an SQLite database table
* `View` the table in the web browser
* `Update` individual fields in the table
* `Delete` individual rows in the table
* `Download` the updated table data as a new CSV file

By implementing these [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) (Create, Read, Update, Delete) operations in each framework, I hope to get a sense of each framework’s unique features and the associated developer experience. To keep things simple, I’ll use SQLite as the database. As a baseline, I’ll start by building the app with what I’m familiar with—FastAPI.

![Polls on Twitter and LinkedIn](/assets/poll.webp "Polls on Twitter and LinkedIn")

I ran polls on the three frameworks on [Twitter](https://x.com/eugeneyan/status/1828447283811402006) and [LinkedIn](https://www.linkedin.com/posts/eugeneyan_if-you-were-building-a-small-web-app-today-activity-7234224078675439617-HX75)

## FastAPI + Jinja + HTML + CSS + JavaScript

Building the app with FastAPI is fairly straightforward ([code](https://github.com/eugeneyan/framework-comparison/tree/main/fastapi)). The key components are:

* `main.py`: Routes for uploading/downloading data, updating fields, deleting rows
* `index.html`: The HTML document that defines the scripts, table, and buttons.
* `style.css`: Visual styling such as column widths, word wrap, scrolling.
* `script.js`: Client-side functionality for uploading the CSV, loading data for display, updating/deleting rows, and downloading the updated data as CSV.

![FastAPI app structure](/assets/fastapi.webp "FastAPI app structure")

Here’s what the web app looks like. While it’s not much to look at aesthetically, it meets our requirements above. I’ve deliberately kept visual styling to a minimum (for the current and later apps) to keep the focus on the frameworks and functionality instead of design.

![FastAPI web app](/assets/fastapi-app.webp "FastAPI web app")

## FastHTML

To learn FastHTML, I started by consulting the [docs](https://docs.fastht.ml) and building a simple [ToDo app](https://github.com/eugeneyan/framework-comparison/blob/main/.learning/fasthtml/todo.py) via this [walkthrough](https://docs.fastht.ml/tutorials/by_example.html#full-example-1---todo-app). For help with unfamiliar components, I relied on Cursor by providing links to relevant docs such as [ft components](https://docs.fastht.ml/explains/explaining_xt_components.html), [htmx](https://docs.fastht.ml/api/components.html), [pico.css](https://docs.fastht.ml/api/pico.html) as context. With FastHTML, I could implement the entire app within a single `main.py` and a small `style.css` ([code](https://github.com/eugeneyan/framework-comparison/tree/main/fasthtml)).

![FastHTML app structure](/assets/fasthtml.webp "FastHTML app structure")

Here’s how the app looks.

![FastHTML web app](/assets/fasthtml-app.webp "FastHTML web app")

After my first iteration above, Hamel graciously offered to pair-program with me to build the app from scratch. He also invited Jeremy Howard—the creator of FastHTML himself—to join us. They taught me several tricks, such as providing Cursor with LLM-friendly documentation for FastHTML ([llms-ctx.txt](https://docs.fastht.ml/llms-ctx.txt)) and FastLite ([html.md](https://answerdotai.github.io/fastlite/index.html.md)). They also shared a [great resource](https://hypermedia.systems) on building simpler apps with htmx and Hyperview. Jeremy even took the time to demonstrate how to build the app in just [50 lines of code](https://gist.github.com/jph00/0590da374a11b8def808c1821abdd42a)!

```
from fasthtml.common import *

db = database(':memory:')
tbl = None
hdrs = (Style('''
button,input { margin: 0 1rem; }
[role="group"] { border: 1px solid #ccc; }
'''), )
app, rt = fast_app(live=True, hdrs=hdrs)

@rt("/")
async def get():
    return Titled("CSV Uploader",
        Group(
            Input(type="file", name="csv_file", accept=".csv"),
            Button("Upload", hx_post="/upload", hx_target="#results",
                   hx_encoding="multipart/form-data", hx_include='previous input'),
            A('Download', href='/download', type="button")
        ),
        Div(id="results"))

def render_row(row):
    vals = [Td(Input(value=v, name=k)) for k,v in row.items()]
    vals.append(Td(Group(Button('delete', hx_get=remove.rt(id=row['id'])),
                   Button('update', hx_post='/update', hx_include="closest tr"))))
    return Tr(*vals, hx_target='closest tr', hx_swap='outerHTML')

@rt
async def download():
    csv_data = [",".join(map(str, tbl.columns_dict))]
    csv_data += [",".join(map(str, row.values())) for row in tbl()]
    headers = {'Content-Disposition': 'attachment; filename="data.csv"'}
    return Response("\n".join(csv_data), media_type="text/csv", headers=headers)

@rt('/update')
def post(d:dict): return render_row(tbl.update(d))

@rt
def remove(id:int): tbl.delete(id)

@rt("/upload")
async def post(csv_file: UploadFile):
    global tbl
    if not csv_file.filename.endswith('.csv'): return "Please upload a CSV file"
    tbl = db.import_file('test', await csv_file.read(), pk='id')
    header = Tr(*map(Th, tbl.columns_dict))
    vals = [render_row(row) for row in tbl()]
    return Table(Thead(header), Tbody(*vals))

serve()
```

And here’s how Jeremy’s app looks:

![Jeremy's version of the FastHTML app](/assets/fasthtml-app-jeremy.webp "Jeremy's version of the FastHTML app")

## Next.JS

To learn Next.js, I did the [React Foundations](https://nextjs.org/learn/react-foundations) and [Next.js](https://nextjs.org/learn/dashboard-app) tutorials. The latter teaches the basics of Next.js through bite-sized, hands-on lessons that build up to a dashboard app. With 16 chapters in the Next.js tutorial, learning and coding along can take some time. Nonetheless, I recommend persisting till at least Chapter 12 on transforming data (in the Next.js tutorial), and enjoyed the gentle learning curve and practical projects.

Here’s how I created the Next.js app template:

```
npx create-next-app@latest
```

Building the same app in Next.js requires considerably more code than the Python versions ([code](https://github.com/eugeneyan/framework-comparison/tree/main/nextjs)). Nonetheless, I found its organization intuitive:

* `api`: Routes for the data table (GET, PUT, DELETE) and file upload/download
* `pages.tsx` and `layout.tsx`: Page-specific and common user interface components
* `components`: Reusable React components like table and upload/download buttons
* `lib`: Utility functions; in this case, there was a single function for SQLite

![Next.js app structure](/assets/next.webp "Next.js app structure")

And here’s how the web app looks. The built-in [Tailwind CSS](https://tailwindcss.com) integration makes the app look a bit more polished compared to the barebones FastAPI and FastHTML apps.

![Next.js web app](/assets/next-app.webp "Next.js web app")

## SvelteKit

To learn Svelte, I went through part of their [tutorial](https://learn.svelte.dev/tutorial/welcome-to-svelte) that comes with an online interpreter. The tutorial has four parts: (i) Basic Svelte, (ii) Advanced Svelte, (iii) Basic SvelteKit, and (iv) Advanced SvelteKit. I completed the sections on basic Svelte and basic SvelteKit and jumped into building the app ([code](https://github.com/eugeneyan/framework-comparison/tree/main/svelte)).

To create the SvelteKit app template, I ran the following:

```
npm create svelte@latest my-app
```

Like Next.js, the template for SvelteKit has several directories and moving parts:

* `components`: Reusable Svelte components such as data table and upload buttons
* `api.ts` and `db.ts`: Functions for the API to fetch, update, and delete data (`api.ts`) as well as query and run updates on the SQLite database (`db.ts`)
* `routes`: Routes for table (GET), rows (PUT, DELETE), and upload/download
* `+page.svelte`: Main page of the application
* `app.html`: Entry point and main HTML file

![SvelteKit app structure](/assets/svelte.webp "SvelteKit app structure")

Here’s how the app looks. One slight deviation: I played with combining the “choose file” and “upload” functionality into a single button, thus removing the “Upload CSV” button.

![SvelteKit web app](/assets/svelte-app.webp "SvelteKit web app")

## FastAPI + Svelte

I also took a stab at building an app with FastAPI as the backend and Svelte for the frontend ([code](https://github.com/eugeneyan/framework-comparison/tree/main/fastapi+svelte)). All functionality and APIs resided in `main.py` while frontend UI and API interactions were handled by `+page.svelte` and `api.ts` respectively. To run the app, I had to start both the FastAPI server and the Svelte development server.

![FastAPI + Svelte app structure](/assets/fastapi-svelte.webp "FastAPI + Svelte app structure")

And here’s what the web app looks like. (I reverted the upload functionality to match the original FastAPI app that had a separate “Upload CSV” button.)

![FastAPI + Svelte web app](/assets/fastapi-svelte-app.webp "FastAPI + Svelte web app")

The main challenge here was coordinating communication between both servers during development. In a production setting, the Svelte app would be compiled and served statically with API requests sent to the FastAPI backend.

• • •

## Aside: How will coding assistants influence builders?

This exercise got me thinking about how coding assistants—powered by LLMs trained on internet data—could influence the choices we make as builders. For example, would LLM-based coding assistants be as effective with niche or newer frameworks such as Svelte and FastHTML? While the tweet below may be an exaggeration, it raises a valid concern.

> It brings me no pleasure to say this, but Svelte is dead because LLM base models are better at writing React. — [Jess Martin](https://x.com/jessmartin/status/1822026807643910149)

Given React and Next’s wider use and longer history, it’s likely most LLMs are trained on more React and Next code than Svelte code. Ditto for FastHTML. This could lead to coding assistants being more effective when working with and suggesting code for established frameworks such as FastAPI, React, and Next.js.

As an anecdote, I had an easier time using Cursor + Claude to build the app in FastAPI and Next.js, and a harder time with FastHTML and SvelteKit. Since FastHTML is barely a couple weeks old (at the time of writing), its code and docs likely hasn’t made its way into the training data of most LLMs yet, explaining their limited proficiency with FastHTML.

To address this issue, Jeremy Howard (creator of FastHTML) has made the effort to provide [llms.txt](https://docs.fastht.ml/llms.txt) and [llms-ctx.txt](https://docs.fastht.ml/llms-ctx.txt) that have been optimized for in-context learning. Similarly, Rich Harris (who works on Svelte at Vercel) [plans](https://x.com/Rich_Harris/status/1832793044216582605) to publish more LLM-friendly documentation for Svelte. Victor Dibia has also [written](https://newsletter.victordibia.com/i/106997987/developer-habits-driven-by-generative-ai) about how coding assistants may affect developer habits and choices, and how we need to write docs for both humans and machines.

Time will tell how effective these efforts are in addressing the cold-start problem for newer or more niche frameworks in coding assistants.

• • •

This was a fun exercise to gain familiarity with FastHTML, Next.js, and SvelteKit. All the code can be found [here](https://github.com/eugeneyan/framework-comparison). (I’m a beginner in frontend so please forgive any bad practices!) Personally, I’m looking forward to building more with TypeScript, which I haven’t used extensively since building [ApplyingML.com](http://applyingml.com) years ago.

What resources have you found useful in learning how to build with Next.js or Svelte? Please comment below or [dm me](https://twitter.com/eugeneyan)!

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Sep 2024). Building the Same App Using Various Web Frameworks. eugeneyan.com.
> https://eugeneyan.com/writing/web-frameworks/.

or

```
@article{yan2024frameworks,
  title   = {Building the Same App Using Various Web Frameworks},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2024},
  month   = {Sep},
  url     = {https://eugeneyan.com/writing/web-frameworks/}
}
```

  
Share on: 

![](/assets/icon-twitter.svg)

![](/assets/icon-linkedin.svg)

![](/assets/bluesky.svg)

![](/assets/icon-facebook.svg)

![](/assets/icon-mail.svg)

---

  

Browse related tags: [
[learning](/tag/learning/)
[engineering](/tag/engineering/)
[python](/tag/python/)
[🛠](/tag/🛠/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Evaluating the Effectiveness of LLM-Evaluators (aka LLM-as-Judge)](/writing/llm-evaluators/)
[Weights & Biases LLM-Evaluator Hackathon - Hackathon Judge »](/speaking/hackathon-judge/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---