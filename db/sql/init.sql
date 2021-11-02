USE challenge;

CREATE TABLE movies(
	id int NOT NULL,
	imdb_id int,
	tmdb_id int,
	title varchar(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE genres(
	movie_id int NOT NULL,
	genre varchar(255) NOT NULL,
	FOREIGN KEY (movie_id) REFERENCES movies(id)
);

CREATE TABLE ratings(
	user_id int NOT NULL,
	movie_id int NOT NULL,
	rating float NOT NULL,
	timestamp int NOT NULL,
	FOREIGN KEY (movie_id) REFERENCES movies(id)
)

CREATE TABLE tags(
	user_id int NOT NULL,
	movie_id int NOT NULL,
	tag varchar(255) NOT NULL,
	timestamp int NOT NULL,
	FOREIGN KEY (movie_id) REFERENCES movies(id)
)




