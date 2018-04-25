CREATE TABLE audioentries(
id serial PRIMARY KEY,
author text not null,
date date not null default CURRENT_DATE,
description text,
hyperlink text not null,
tags text[]
);


-- Example insertion:

insert into audioentries(
author,
description,
tags,
hyperlink
) values (
'Evan Garrett',
 'This is a cool thing',
'{Politics, Society}',
'https://audiobooks.com/thisone.mp3');