import re

head = '''\n<head>
<style>
mark {
background-color: white;
color: red;
border: 1px solid black;
padding: 0 2px;
font-size: 90%;
}
</style>

<meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title>HTML</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="apple-touch-icon" href="apple-touch-icon.png">

        <link rel="stylesheet" href="/static/css/bootstrap.min.css">
        <style>
            body {
                padding-top: 50px;
                padding-bottom: 20px;
            }
        </style>
        <link rel="stylesheet" href="../static/css/bootstrap-theme.min.css">
        <link rel="stylesheet" href="../static/css/main.css">
        <link rel="stylesheet" type="text/css" href="../static/bootstrap-select/dist/css/bootstrap-select.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.12.4/css/bootstrap-select.min.css">

        <script src="/static/js/vendor/modernizr-2.8.3-respond-1.4.2.min.js"></script>

	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

	<title>rstWeb - Structure editor</title>
	<link rel="stylesheet" href="../static/rstWeb/css/rst.css" type="text/css" charset="utf-8"/>
    <link rel="stylesheet" href="../static/rstWeb/css/font-awesome-4.2.0/css/font-awesome.min.css"/>
    <script src="../static/rstWeb/script/jquery-1.11.3.min.js"></script>
    <script src="../static/rstWeb/script/jquery-ui.min.js"></script>
    <script src="../static/rstWeb/script/nav.js"></script>

</head>

<body>
    <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="../../index.html">Главная</a>
          <a class="navbar-brand" href="aboutRST.html">О Теории</a>
          <a class="navbar-brand" href="search.html">Поиск</a>
      <a class="navbar-brand" href="corpus.html">Корпус</a>
          <a class="navbar-brand" href="download.html">Скачать</a>
          <a class="navbar-brand" href="contact.html">Контакты</a>
        </div>
        <div id="navbar" class="navbar-collapse collapse">
        </div><!--/.navbar-collapse -->
      </div>
    </nav>\n
'''

# Открываем входной файл
source = open('./source/3.html', 'r', encoding='utf-8').read()
buttons = [re.split('</button>', x)[0] for x in re.split('<button', source)[1:]]
for b in buttons:
    source = source.replace(b, '')

source = source.replace('</button>', '').replace('<button', '')

found = re.findall('<head>.*?<div class="canvas">	<p>Document: <b>', source, re.DOTALL)[0]

source = re.sub(re.escape(found), '<div class="canvas">\n<p>Document: <b>', source, re.DOTALL)

source = re.sub('<script src="./script/jquery.jsPlumb-1.7.5-min.js"></script>',
                '<script src="../static/rstWeb/script/jquery.jsPlumb-1.7.5-min.js"></script>', source)

source = re.sub('jsPlumb.makeSource.*?;jsPlumb.connect', 'jsPlumb.connect', source)

source = re.sub(re.escape('>" + select_my_rel(option_type,rel) + "<'), '><mark>" + rel.split(\'_\')[0] + "</mark><',
                source)

source = re.sub("select class='rst_rel'", "form class='rst_rel'", source)
source = re.sub("</mark></select>", "</mark></form>", source)

source = re.sub('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">',
                '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">' + head, source)

source = re.sub('<div id="anim_catch" class="anim_catch">&nbsp;</div>',
                '<div id="anim_catch" class="anim_catch">&nbsp;</div>\n<p/>\n<footer>\n<p>&copy; Ru-RST Group 2017</p>\n</footer>\n</div>',
                source)

# Открываем выходной файл
result = open('./result/3.html', 'w', encoding='utf-8')
result.write(source)