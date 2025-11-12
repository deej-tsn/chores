type User = {
    first_name: string;
    second_name: string;
    email: string;
    colour: string;
}

type Token = {
    access_token : string,
    token_type : string
}

type TokenData = {
    sub : string, 
    first_name : string,
    second_name : string,
    colour : string,
    iat : Date,
    exp : Date
}

export type {
    User,
    Token,
    TokenData
}