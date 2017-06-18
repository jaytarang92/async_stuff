from aiohttp.web import (View, Response, json_response, Application, run_app)
from aiohttp import ClientSession
from asyncio import get_event_loop
from asyncio import set_event_loop_policy
from uvloop import EventLoopPolicy

proxy_config = 'http://throw.proxy.here.com'
url_to_target = [
    'https://jsonplaceholder.typicode.com/posts',
    'http://surveycodebot.com/person/generate'
    ]

# this would go in a different file but keep it simple for this example
class JsonGenerator:

    # Get a json object from a website
    async def get_response(self, url):
        """
            @param `url`: url to request data from
        """
        async with ClientSession() as session:
            async with session.get(url, proxy=proxy_config) as response:
                # if we don't `await` here we get the generator and not the json
                resp = await response.json()
                return resp

    # loops `get_response` to get more than 1 object | response
    async def get_responses(self, url_list):
        """
            @param `url_list`: list of urls to request data from
        """
        json_responses = []
        # array for gathering all responses
        for url in url_list:
            json_responses.append(await self.get_response(url))
        return json_responses


# class to handle '/'
class HomePage(View):

    async def get(self):
        return Response(text="<h1>Maybe render a index.html here!</h1>",
                           content_type='text/html')


class GetData(View):

    async def get(self):
        # initiate the Generate class and call get_responses
        json_object = await JsonGenerator().get_response(url_to_target[0])
        return json_response(json_object)

    async def post(self):
        urls = []
        # for loop to create a list of urls
        for _ in range(0,10):
            urls.append(url_to_target[0])
            json_objects = await JsonGenerator().get_responses(urls)
        return json_response(json_objects)

def make_app(close=False):
    app = Application()
    app.router.add_get('/', HomePage)
    app.router.add_post('/multiple', GetData)
    app.router.add_get('/single', GetData)
    set_event_loop_policy(EventLoopPolicy())
    loop = get_event_loop()
    if close:
        loop.close()
    loop.create_server(run_app(app, port=8888))
    print("======= Serving on http://127.0.0.1:8080/ ======")
    loop.run_forever()

if __name__ == "__main__":
    try:
        make_app()
    except KeyboardInterrupt:
        make_app(close=True)
