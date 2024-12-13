INSERT INTO brands(brand_name)
VALUES
    (
         'Botanee'
    ),
    (
     'Paco Rabanne'
    ),
    (
     'DIOR'
    );
INSERT INTO categories(name)
VALUES
    (
     'Бад для здоровья волос и ногтей'
    ),
    (
     'Парфюмерная косметика'
    );

INSERT INTO products(name, description, price, stock_quantity, category_id, brand_id)
VALUES
    (
     'BOTANEE коллаген, витамиин C',
    'Порошковый коллаген со вкусом лимона-лайма Botanee - это уникальное спортивное питание, созданное специально для поддержания здоровья кожи, волос, ногтей и суставов. Этот продукт является идеальным комбинированным решением для тех, кто хочет получить полезные витамины и минералы, а также укрепить свой организм.',
    10,
     20,
     1,
     1
    ),
    (
     'DIOR sauvage',
     'Новое творение от Dior: яркий харизматичный аромат цвета полуночного неба. Новая высококонцентрированная интерпретация Sauvage, сочетающая экстремальную свежесть и теплые восточные ноты, раскрывается при соприкосновении аромата с кожей. Франсуа Демаши, парфюмер-создатель Dior, вдохновлялся нетронутыми уголками дикой природы под полуночным небом, когда воздух наполняется ароматом потрескивающего в огне дерева.',
     120,
     20,
     2,
     3
    ),
    (
     'RABANNE invictus victory elixir',
    'Квинтэссенция насыщенности во вселенной Invictus от Paco Rabanne. Обновленный манифест о воле к безграничным достижениям. Пришло время запечатлеть момент и ощутить себя в лучах славы с Invictus Victory Elixir, новым эффектным ароматом для мужчин. Пора насладиться моментом истинного величия. Многогранная, яркая, стойкая композиция сочетает в себе пряные древесные аккорды и обжигающую свежесть, являя собой новое интенсивное воплощение культового аромата Paco Rabanne. Никогда не останавливайся на достигнутом с Invictus Victory Elixir от Paco Rabanne.',
     139,
     10,
     2,
     2
    );
