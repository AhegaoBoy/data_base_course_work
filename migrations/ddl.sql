ALTER TABLE public.customers ADD "password" varchar(255) NULL;

ALTER TABLE public.products ADD category_id int4 NULL;

ALTER TABLE public.products ADD brand_id int4 NULL;

ALTER TABLE public.categories ADD "name" varchar NULL;

-- Drop table

-- DROP TABLE public.roles;

CREATE TABLE public.roles (
	id serial4 NOT NULL,
	"role" varchar NULL,
	CONSTRAINT roles_pkey PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE public.roles OWNER TO postgres;
GRANT ALL ON TABLE public.roles TO postgres;

-- Drop table

-- DROP TABLE public.customers;

CREATE TABLE public.customers (
	"name" varchar NULL,
	"role" int4 NULL,
	id int4 DEFAULT nextval('customers_new_id_seq'::regclass) NOT NULL,
	"password" varchar(255) NULL,
	balance numeric DEFAULT 0 NULL,
	CONSTRAINT pr_key1 PRIMARY KEY (id),
	CONSTRAINT customer_role FOREIGN KEY ("role") REFERENCES public.roles(id)
);

-- Permissions

ALTER TABLE public.customers OWNER TO postgres;
GRANT ALL ON TABLE public.customers TO postgres;

ALTER TABLE public.categories ADD id serial4 NOT NULL;

ALTER TABLE public.reviews ADD product_id int4 NULL;

ALTER TABLE public.order_items ADD product_id int4 NULL;

ALTER TABLE public.reviews ADD "comment" text NULL;

ALTER TABLE public.reviews ADD id int4 DEFAULT nextval('rewiewes_id_seq'::regclass) NOT NULL;

ALTER TABLE public.orders ADD order_date timestamp NULL;

ALTER TABLE public.order_items ADD order_id int4 NULL;

-- Drop table

-- DROP TABLE public.brands;

CREATE TABLE public.brands (
	id serial4 NOT NULL,
	brand_name varchar NULL,
	CONSTRAINT brands_pkey PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE public.brands OWNER TO postgres;
GRANT ALL ON TABLE public.brands TO postgres;

ALTER TABLE public.customers ADD "role" int4 NULL;

-- Drop table

-- DROP TABLE public.products;

CREATE TABLE public.products (
	"name" varchar NULL,
	description text NULL,
	price numeric NULL,
	stock_quantity int4 NULL,
	category_id int4 NULL,
	brand_id int4 NULL,
	id int4 DEFAULT nextval('products_new_id_seq'::regclass) NOT NULL,
	cart_quantity int4 DEFAULT 0 NULL,
	CONSTRAINT pr_key PRIMARY KEY (id),
	CONSTRAINT fk_brands FOREIGN KEY (brand_id) REFERENCES public.brands(id),
	CONSTRAINT fk_categories FOREIGN KEY (category_id) REFERENCES public.categories(id)
);

-- Permissions

ALTER TABLE public.products OWNER TO postgres;
GRANT ALL ON TABLE public.products TO postgres;

-- Drop table

-- DROP TABLE public.orders;

CREATE TABLE public.orders (
	id serial4 NOT NULL,
	customer_id int4 NULL,
	order_date timestamp NULL,
	order_summ numeric NULL,
	order_state varchar(20) NULL,
	CONSTRAINT orders_pkey PRIMARY KEY (id),
	CONSTRAINT orders_cus_fk FOREIGN KEY (customer_id) REFERENCES public.customers(id)
);

-- Permissions

ALTER TABLE public.orders OWNER TO postgres;
GRANT ALL ON TABLE public.orders TO postgres;

ALTER TABLE public.order_items ADD quantity int4 NULL;

ALTER TABLE public.products ADD stock_quantity int4 NULL;

ALTER TABLE public.reviews ADD rate numeric NULL;

-- Drop table

-- DROP TABLE public.reviews;

CREATE TABLE public.reviews (
	id int4 DEFAULT nextval('rewiewes_id_seq'::regclass) NOT NULL,
	product_id int4 NULL,
	customer_id int4 NULL,
	rate numeric NULL,
	"comment" text NULL,
	"date" timestamp NULL,
	CONSTRAINT rewiewes_pkey PRIMARY KEY (id),
	CONSTRAINT rew_fk FOREIGN KEY (customer_id) REFERENCES public.customers(id),
	CONSTRAINT rew_prod_fk FOREIGN KEY (product_id) REFERENCES public.products(id)
);

-- Permissions

ALTER TABLE public.reviews OWNER TO postgres;
GRANT ALL ON TABLE public.reviews TO postgres;

ALTER TABLE public.orders ADD customer_id int4 NULL;

ALTER TABLE public.order_items ADD id serial4 NOT NULL;

ALTER TABLE public.products ADD description text NULL;

ALTER TABLE public.orders ADD id serial4 NOT NULL;

ALTER TABLE public.products ADD id int4 DEFAULT nextval('products_new_id_seq'::regclass) NOT NULL;

ALTER TABLE public.orders ADD order_state varchar(20) NULL;

ALTER TABLE public.brands ADD brand_name varchar NULL;

ALTER TABLE public.brands ADD id serial4 NOT NULL;

ALTER TABLE public.orders ADD order_summ numeric NULL;

ALTER TABLE public.products ADD "name" varchar NULL;

ALTER TABLE public.products ADD cart_quantity int4 DEFAULT 0 NULL;

ALTER TABLE public.roles ADD "role" varchar NULL;

ALTER TABLE public.customers ADD id int4 DEFAULT nextval('customers_new_id_seq'::regclass) NOT NULL;

ALTER TABLE public.products ADD price numeric NULL;

ALTER TABLE public.customers ADD "name" varchar NULL;

-- Drop table

-- DROP TABLE public.categories;

CREATE TABLE public.categories (
	id serial4 NOT NULL,
	"name" varchar NULL,
	CONSTRAINT categories_pkey PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE public.categories OWNER TO postgres;
GRANT ALL ON TABLE public.categories TO postgres;

-- Drop table

-- DROP TABLE public.order_items;

CREATE TABLE public.order_items (
	id serial4 NOT NULL,
	order_id int4 NULL,
	product_id int4 NULL,
	quantity int4 NULL,
	unitprice numeric NULL,
	CONSTRAINT order_items_pkey PRIMARY KEY (id),
	CONSTRAINT items_orders_fk FOREIGN KEY (order_id) REFERENCES public.orders(id),
	CONSTRAINT items_products_fk FOREIGN KEY (product_id) REFERENCES public.products(id)
);

-- Permissions

ALTER TABLE public.order_items OWNER TO postgres;
GRANT ALL ON TABLE public.order_items TO postgres;

ALTER TABLE public.reviews ADD customer_id int4 NULL;

ALTER TABLE public.customers ADD balance numeric DEFAULT 0 NULL;

ALTER TABLE public.reviews ADD "date" timestamp NULL;

ALTER TABLE public.order_items ADD unitprice numeric NULL;

ALTER TABLE public.roles ADD id serial4 NOT NULL;