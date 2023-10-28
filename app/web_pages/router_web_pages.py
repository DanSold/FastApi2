from fastapi import APIRouter, Request, Form, HTTPException, status, Depends, Response
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
import dao
from app.auth.schemas import DishDetails, DishAppended
from app.auth import dependencies
from app.auth.auth_lib import AuthHandler, AuthLibrary

router = APIRouter(
    prefix='/web',
    tags=['menu', 'landing'],
    include_in_schema=False
)

templates = Jinja2Templates(directory='app/templates')


@router.post('/search')
@router.get('/menu')
async def get_menu(request: Request, dish_name: str = Form(None), user=Depends(dependencies.get_current_user_optional)):
    all_dishes = await dao.fetch_dishes()
    if not all_dishes:
        context = {
            'request': request,
            'title': f'Search results for {dish_name}' if dish_name else 'Recipes',
            'menu': [],
            'user': user,
        }

        return templates.TemplateResponse(
            'menu.html',
            context=context,
        )
    filtered_menu = []
    if dish_name:
        for dish in all_dishes:
            if dish_name.lower() in dish.name.lower():
                filtered_menu.append(dish)
    ids = {dish.__dict__['author'] for dish in all_dishes}
    authors = await dao.get_users_by_ids(ids)
    print(authors[0].__dict__)
    context = {
        'request': request,
        'title': f'Search results for {dish_name}' if dish_name else 'Our menu',
        'menu': filtered_menu if dish_name else all_dishes,
        'user': user,
    }

    return templates.TemplateResponse(
        'menu.html',
        context=context,
    )


@router.get('/user_dishes')
async def get_user_dishes(request: Request, user=Depends(dependencies.get_current_user_optional)):
    menu = await dao.get_dish_by_author(user.id)
    context = {
        'request': request,
        'title': 'My dishes',
        'menu': menu,
        'user': user,
    }

    return templates.TemplateResponse(
        'menu.html',
        context=context,
    )


@router.get('/create')
async def create_dish(request: Request, user=Depends(dependencies.get_current_user_optional)):
    context = {
        'request': request,
        'user': user,
        'title': 'Create dish'
    }
    return templates.TemplateResponse(
        'create.html',
        context=context
    )


@router.post('/create/add_dish')
async def add_dish(request: Request, user=Depends(dependencies.get_current_user_optional),
                   name: str = Form(...), recipe: str = Form(...), picture: str = Form(...)):
    await dao.create_dish(
        name=name,
        recipe=recipe,
        author=user.id,
        picture=picture
    )
    menu = await dao.fetch_dishes()
    context = {
        'request': request,
        'menu': menu,
        'user': user
    }
    result = templates.TemplateResponse(
        'menu.html',
        context=context,
    )
    return result

@router.get('/error')
async def web_error(request: Request, user=Depends(dependencies.get_current_user_optional)):
    context = {
        'request': request,
        'user': user,
        'content': f'Incorrect login or password'
    }
    return templates.TemplateResponse(
        '400.html',
        context=context
    )

@router.get('/user')
async def open_user(request: Request):
    context = {
        'request': request,
        'title': 'Registration',

    }
    template_response = templates.TemplateResponse(
        'registration.html',
        context=context,
    )
    return template_response


@router.get('/user/login_web')
async def open_user(request: Request):
    context = {
        'request': request,
        'title': 'Login',

    }
    template_response = templates.TemplateResponse(
        'login_web.html',
        context=context,
    )
    return template_response


@router.post('/user/register')
async def register_final(request: Request,
                         name: str = Form(None),
                         login: EmailStr = Form(None),
                         password: str = Form(None),
                         ):
    if not all([name, login, password]):
        context = {
            'request': request,
            'title': 'Error',
            'content': f'User {login} already exists',
        }
        return templates.TemplateResponse(
            '400.html',
            context=context,
            status_code=status.HTTP_406_NOT_ACCEPTABLE
        )
    is_login_already_used = await dao.get_user_by_login(login)
    menu = await dao.fetch_dishes()
    if is_login_already_used:
        context = {
            'request': request,
            'title': 'Error',
            'content': f'User {login} already exists',
        }
        return templates.TemplateResponse(
            '400.html',
            context=context,
            status_code=status.HTTP_406_NOT_ACCEPTABLE
        )
    hashed_password = await AuthHandler.get_password_hash(password)
    user_data = await dao.create_user(
        name=name,
        login=login,
        password=hashed_password,
        moderator=False
    )
    token = await AuthHandler.encode_token(user_data[0])
    context = {
        'request': request,
        'title': 'Title',
        'menu': menu,
        'user': user_data,
    }
    template_response = templates.TemplateResponse(
        'menu.html',
        context=context,
    )
    template_response.set_cookie(key='token', value=token, httponly=True)
    return template_response



@router.post('/user/login_web/login')
async def login(request: Request, login: EmailStr = Form(...), password: str = Form(...)):
    user = await AuthLibrary.authenticate_user_web(login=login, password=password)
    if not user:
        context = {
            'request': request,
            'user': user,
            'content': f'Incorrect login or password'
        }
        return templates.TemplateResponse(
            '400.html',
            context=context
        )
    token = await AuthHandler.encode_token(user.id)
    menu = await dao.fetch_dishes()
    context = {
        'request': request,
        'title': 'Login',
        'menu': menu,
        'user': user,
    }
    response = templates.TemplateResponse(
        'menu.html',
        context=context,
    )
    response.set_cookie(key='token', value=token, httponly=True)
    return response


@router.post('/logout')
@router.get('/logout')
async def logout(request: Request, response: Response, user=Depends(dependencies.get_current_user_optional)):
    menu = await dao.fetch_dishes()
    context = {
        'request': request,
        'title': 'Recipes',
        'menu': menu,
        'user': user
    }
    result = templates.TemplateResponse(
        'menu.html',
        context=context,
    )
    result.delete_cookie('token')
    return result


@router.get('/menu/delete_dish/{dish_id}')
async def delete_dish(request: Request, dish_id: int, user=Depends(dependencies.get_current_user_optional)):
    await dao.delete_dish(dish_id=dish_id)
    menu = await dao.fetch_dishes()
    context = {
        'request': request,
        'menu': menu,
        'user': user
    }
    result = templates.TemplateResponse(
        'menu.html',
        context=context,
    )
    return result


@router.get('/menu/edit_dish/{dish_id}')
async def open_user(request: Request, dish_id: int):
    dish = await dao.get_dish_by_id(dish_id=dish_id)
    context = {
        'request': request,
        'title': 'Edit dish',
        'dish': dish
    }

    print(context)

    template_response = templates.TemplateResponse(
        'edit_dish.html',
        context=context,
    )
    return template_response


@router.post('/menu/edit_dish/{dish_id}/update_dish')
async def edit_dish(request: Request, dish_id: int, user=Depends(dependencies.get_current_user_optional),
                    name: str = Form(...),
                    recipe: str = Form(...),
                    picture: str = Form(...)
                    ):
    print(dish_id)
    await dao.update_dish(dish_id=dish_id, name=name, recipe=recipe, picture=picture)
    menu = await dao.fetch_dishes()
    context = {
        'request': request,
        'menu': menu,
        'user': user
    }
    result = templates.TemplateResponse(
        'menu.html',
        context=context,
    )
    return result
