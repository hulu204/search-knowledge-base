---
title: 'https://eugeneyan.com//writing/fastapi-html-checkbox-download/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/fastapi-html-checkbox-download/
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

# Adding a Checkbox & Download Button to a FastAPI-HTML app

[
[engineering](/tag/engineering/)
[python](/tag/python/)
[til](/tag/til/)
]
 · 3 min read

In a previous [post](/writing/how-to-set-up-html-app-with-fastapi-jinja-forms-templates/), I shared about how to build a simple HTML app using `FastAPI`. Here, we’ll extend that app by adding functionality for checkboxes and a download button.

> Try it out with the GitHub repo here: [`fastapi-html`](https://github.com/eugeneyan/fastapi-html)

## Let’s allow users to alter results

To demonstrate this, we’ll create a checkbox to multiply the input number by two, before spelling it out.

Here’s the [`HTML`](https://github.com/eugeneyan/fastapi-html/blob/master/templates/checkbox.html) for it, where we include a new input of type `checkbox` and its label. Note the `name` (`multiply_by_2`) and `value` (`True`) params—we’ll use it later in the post request.

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sample Form</title>
</head>
<body>
<form method="post">
    <input type="number" name="num" value=""/>
    <input type="checkbox" id="multiply_by_2" name="multiply_by_2" value="True">
    <label for="multiply_by_2">Multiply by 2&nbsp;</label>
    <input type="submit">
</form>
<p>Result: </p>
</body>
</html>
```

We’ll update our post request to take an additional param `multiply_by_2` (from `name`). By default, the value is `False`; but if we check the checkbox, we get the value of `True` (from `value`). This boolean is passed into [`spell_number`](https://github.com/eugeneyan/fastapi-html/blob/master/src/model.py) which handles the logic.

```
@app.post('/checkbox')
def form_post(request: Request, num: int = Form(...), multiply_by_2: bool = Form(False)):
    result = spell_number(num, multiply_by_2)
    return templates.TemplateResponse('checkbox.html', context={'request': request, 'result': result, 'num': num})
```

Here are the results with and without checking the option.

![Results before and after multiplying by 2](/assets/multiply-by-2.webp "Results before and after multiplying by 2")

Results with and without the "Multiply by 2" option

## Let’s allow users to download results

After users view the results, they might want to download it. (In this scenario, it’s a really simple result. Nonetheless, a real app could provide results such as a csv of fraudulent purchases, a pdf report, or an ipython notebook.)

To achieve this, we’ll add a [download](https://github.com/eugeneyan/fastapi-html/blob/master/templates/download.html) button. Notice that we now have *two* inputs of type `submit`. As usual, we’ll use the `name` and `value` params.

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sample Form</title>
</head>
<body>
<form method="post">
    <input type="number" name="num" value=""/>
    <input type="checkbox" id="multiply_by_2" name="multiply_by_2" value="True">
    <label for="multiply_by_2">Multiply by 2&nbsp;</label>
    <input type="submit" name="action" value="convert">
    <input type="submit" name="action" value="download">
</form>
<p>Result: </p>
</body>
</html>
```

We’ll update the post request with some basic logic to either return the result via HTML, or to download the file. Note that for `FileResponse` to work, we’ll need to install the `aiofiles` package.

```
@app.post('/download')
def form_post(request: Request, num: int = Form(...), 
              multiply_by_2: bool = Form(False), action: str = Form(...)):
    if action == 'convert':
        result = spell_number(num, multiply_by_2)
        return templates.TemplateResponse('download.html', context={'request': request, 'result': result, 'num': num})
    elif action == 'download':
        # Requires aiofiles
        result = spell_number(num, multiply_by_2)
        filepath = save_to_text(result, num)
        return FileResponse(filepath, media_type='application/octet-stream', filename='{}.txt'.format(num))
```

Here’s how the downloaded file looks like. It is named after the input query `1234.txt`. The results will be the input query spelt out (possibly multiply by two).

![The additional download button and the downloaded file](/assets/multiply-and-download.webp "The additional download button and the downloaded file")

The downloaded file (1234.txt) and the result (with "Multiply by 2")

> Try it out with the GitHub repo here: [`fastapi-html`](https://github.com/eugeneyan/fastapi-html)

> Next, we update our FastAPI app to let users:  
>   
> • Select options via a checkbox  
> • Download results via a download button <https://t.co/jFUmiMaud4>
>
> — Eugene Yan (@eugeneyan) [August 7, 2020](https://twitter.com/eugeneyan/status/1291568760713703425?ref_src=twsrc%5Etfw)

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Aug 2020). Adding a Checkbox & Download Button to a FastAPI-HTML app. eugeneyan.com.
> https://eugeneyan.com/writing/fastapi-html-checkbox-download/.

or

```
@article{yan2020fastapi2,
  title   = {Adding a Checkbox & Download Button to a FastAPI-HTML app},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2020},
  month   = {Aug},
  url     = {https://eugeneyan.com/writing/fastapi-html-checkbox-download/}
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
[engineering](/tag/engineering/)
[python](/tag/python/)
[til](/tag/til/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« What I Did Not Learn About Writing In School](/writing/what-i-did-not-learn-about-writing-in-school/)
[Unpopular Opinion: Data Scientists Should be More End-to-End »](/writing/end-to-end-data-science/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---