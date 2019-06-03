from bs4 import BeautifulSoup

html_doc = """
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Sample Web Page</title>
</head>

<body>
  <div id="section-1">
    <h3 data-hello="hi">Hello</h3>
    <img src="https://source.unsplash.com/200x200/?nature,water">
    <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. A suscipit, ipsa, cumque sint accusamus fugit aspernatur
      aliquid sapiente dignissimos ad doloribus. Incidunt laudantium nisi id cupiditate eos iste dicta non.</p>
  </div>

  <div id="section-2">
    <ul class="items">
      <li class="item"><a href="#">Item 1</a></li>
      <li class="item"><a href="#">Item 2</a></li>
      <li class="item"><a href="#">Item 3</a></li>
      <li class="item"><a href="#">Item 4</a></li>
      <li class="item"><a href="#">Item 5</a></li>
      <li class="item"><a href="#">Item 6</a></li>
    </ul>
  </div>
</body>

</html>
"""

soup = BeautifulSoup(html_doc, 'html.parser')

# print(soup.body)
# print(soup.head)
# print(soup.head.title)

# find() - finds the first instance
# el = soup.find('div')

# find_all or findAll() - returns an array

# el = soup.find_all('div')

# el = soup.find_all('div')[1]

# parse by id
# el = soup.find(id='section-2')


# parse by class (class is a reserved word in python so use class_)

# el = soup.find(class_='items')

# find by attribute value
# el = soup.find(attrs={"data-hello": "hi"})

# select - returns a list - unless you use [x]
# find by css selector
# el = soup.select('#section-2')
# el = soup.select('.item')
# el = soup.select('.item')[2]

# just return the text of an attribute

# el = soup.find(class_='item').get_text()

# for item in soup.select('.item'):
# print(item.get_text())

# print(el)


# Navigation


# for (num, item) in enumerate(soup.body.contents):
#     print(num+1)
#     print(item)


# el = soup.body.contents[1]
# print(el)
# print('***************')


# el = soup.body.contents[1].contents[1]

# print(el)
# print('***************')

# el = soup.body.contents[1].contents[1].find_next_sibling()

# print(el)
# print('***************')


# el = soup.find(id='section-2').find_previous_sibling()


# el = soup.find(class_='item').find_parent()


# find the next paragraph agter the first h3
el = soup.find('h3').find_next_sibling('p')

print(el)
