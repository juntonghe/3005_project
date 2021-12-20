-- Before create the tables
-- I have created a database named Book

-- Create the tables
CREATE TABLE Users(
    user_nickname VARCHAR(100),
	user_password VARCHAR(100),
	user_type VARCHAR(100),
    user_firstname VARCHAR(100),
    user_lastname VARCHAR(100),
	user_dob VARCHAR(100),
	user_billing VARCHAR(100),
	user_shipping VARCHAR(100),	
	PRIMARY KEY(user_nickname),
	CHECK(user_type='customer' Or user_type='owner')
);

CREATE TABLE Author(
    author_id INT,
    author_firstname VARCHAR(100),
    author_lastname VARCHAR(100),
	PRIMARY KEY(author_id)
);
Insert into author(author_id, author_firstname, author_lastname) values(1, 'John', 'Milton');
Insert into author(author_id, author_firstname, author_lastname) values(2, 'Charles', 'Olson');

CREATE TABLE Genre(
    genre_id INT,
    genre_name VARCHAR(100),
	PRIMARY KEY(genre_id)
);
Insert into Genre(genre_id, genre_name) values(1, 'Science');
Insert into Genre(genre_id, genre_name) values(2, 'Biology');

CREATE TABLE Publisher(
    publisher_id INT,
    publisher_name VARCHAR(100),
    publisher_address VARCHAR(100),
	publisher_email VARCHAR(100),
	publisher_phone VARCHAR(100),
	publisher_banking VARCHAR(100),
	PRIMARY KEY(publisher_id)
);
Insert into Publisher(publisher_id,publisher_name,publisher_address,publisher_email,publisher_phone,publisher_banking)
Values(1, 'Oxford', 'Oxford mock address', 'Oxford@gmail.com', '100000', '9999999001');
Insert into Publisher(publisher_id,publisher_name,publisher_address,publisher_email,publisher_phone,publisher_banking)
Values(2, 'Cambridge', 'Cambridge mock address', 'Cambridge@gmail.com', '200000', '9999999002');


CREATE TABLE Book(
    book_isbn INT,
    book_name VARCHAR(100),
    book_pages INT,
	book_price NUMERIC,
	book_percentage NUMERIC,
	book_quantity INT,
	book_threshold INT,
	author_id INT,
	genre_id INT,
	publisher_id INT,
	PRIMARY KEY(book_isbn),
	FOREIGN KEY (author_id) REFERENCES Author(author_id),
	FOREIGN KEY (genre_id) REFERENCES Genre(genre_id),
	FOREIGN KEY (publisher_id) REFERENCES Publisher(publisher_id)
);

CREATE TABLE Basket(
    user_nickname VARCHAR(100),
	book_isbn INT,
    book_num INT,
	PRIMARY KEY(user_nickname, book_isbn),
	FOREIGN KEY (user_nickname) REFERENCES Users(user_nickname),
	FOREIGN KEY (book_isbn) REFERENCES Book(book_isbn)
);

Create Sequence order_id_seq Start With 1 Increment By 1 No minvalue No maxvalue cache 1;
CREATE TABLE "Order"(
    order_id INT,
	user_nickname VARCHAR(100),
	order_totalprice NUMERIC,
	order_billing VARCHAR(100),
	order_shipping VARCHAR(100),	
	PRIMARY KEY(order_id),
	FOREIGN KEY (user_nickname) REFERENCES Users(user_nickname)
);
Alter Table "Order" Alter Column order_id Set Default Nextval('order_id_seq');

CREATE TABLE OrderDetail(
    order_id INT,
	book_isbn INT,
	book_num INT,
	PRIMARY KEY(order_id, book_isbn),
	FOREIGN KEY (order_id) REFERENCES "Order"(order_id),
	FOREIGN KEY (book_isbn) REFERENCES Book(book_isbn)
);

CREATE TABLE OrderTrack(
    order_id INT,
    track_datetime TIMESTAMP,
	track_shipping VARCHAR(100),
	PRIMARY KEY(order_id, track_datetime),
	FOREIGN KEY (order_id) REFERENCES "Order"(order_id)
);

Create Sequence email_id_seq Start With 1 Increment By 1 No minvalue No maxvalue cache 1;
CREATE TABLE Email(
    email_id INT,
    book_isbn INT,
	publisher_id INT,
	book_num INT,
	PRIMARY KEY(email_id),
	FOREIGN KEY (book_isbn) REFERENCES Book(book_isbn),
	FOREIGN KEY (publisher_id) REFERENCES Publisher(publisher_id)
);
Alter Table Email Alter Column email_id Set Default Nextval('email_id_seq');