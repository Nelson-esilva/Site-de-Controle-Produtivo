CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user VARCHAR(100),
    senha VARCHAR(20),
    matricula VARCHAR(30)
);

CREATE TABLE dados_programa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nproduto VARCHAR(100),
    peso VARCHAR(20),
    datai DATE,
    horai TIME,
    dataf DATE,
    horaf TIME,
    marcha BOOLEAN,
    defprod VARCHAR(100),
    motivo  VARCHAR(100),
    acaocorre VARCHAR(100),
    respons VARCHAR(100),
    obs VARCHAR(200)
);
