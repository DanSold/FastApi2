from pydantic import BaseModel, Field, EmailStr
import settings


class AuthDetails(BaseModel):
    name: str = Field(min_length=3, max_length=50, examples=['Barak Obama'])
    login: EmailStr = Field(examples=['login@ukr.net'])
    password: str = Field(min_length=settings.Settings.MIN_PASSWORD_LENGTH, max_length=50, examples=['65dfg6dfb5%&^'])
    moderator: bool = Field(examples=[True])


class AuthRegistered(BaseModel):
    success: bool = Field(examples=[True])
    id: int = Field(examples=[656])
    login: EmailStr = Field(examples=['login@ukr.net'])


class AuthLogin(BaseModel):
    login: EmailStr = Field(examples=['login@ukr.net'])
    password: str = Field(min_length=settings.Settings.MIN_PASSWORD_LENGTH, max_length=50, examples=['65dfg6dfb5%&^'])


class DishDetails(BaseModel):
    name: str = Field(examples=['Borsh'], min_length=settings.Settings.MIN_DISH_NAME_LENGTH,
                      max_length=settings.Settings.MAX_DISH_NAME_LENGTH)
    recipe: str = Field(examples=['Something to something'], max_length=settings.Settings.MAX_DISH_RECIPE_LENGTH)
    author: int = Field(examples=[10])


class DishAppended(BaseModel):
    success: bool = Field(examples=[True])
    name: str = Field(examples=['Borsh'], min_length=settings.Settings.MIN_DISH_NAME_LENGTH,
                      max_length=settings.Settings.MAX_DISH_NAME_LENGTH)
    recipe: str = Field(examples=['Something to something'], max_length=settings.Settings.MAX_DISH_RECIPE_LENGTH)
    author: int = Field(examples=[1])
    picture: str = Field(examples=['https://images.unian.net/photos/2022_09/thumb_files/1200_0_1662892107-3846.jpg'])
