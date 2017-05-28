# Artifact-Auction-Website
A project for Database class

Postgre Sql account: xz2580

web address: 40.114.93.58:8111

Description of part 1:
Our project is a Chinese fine arts auction information search engine that can be used to search for any 
specific type of Chinese fine art work, which has been shown on auction houses such as Sotheby's or 
Christies, by key words of an auction good's features. When users try to search for art works either in 
abstract by a single key word or with full description, all matched results should pop out, showing 
information containing name, lot number at a specific auction, its standard price in US dollar, 
and furthermore, a URL links to the auction good for more details. 
An auction good is unique based on its URL. An auction good belongs to a certain class such as 
calligraphy, painting, ceramic, etc, with other characteristics like color, decoration pattern and mark. 
Also, it can be traced back to a unique time when it was made. An auction house is unique based on its 
name. 

This is an auction evaluation web project that allows you to search through our online database to find 
the auction good you intend to search.
After connecting to the index page, you will be asked to either log in with an account you already created 
or register for another account. You will be automatically signed in after registrattion.
After signing in, you can try to search either by auctions or goods.
In searching by auctions, by selecting a specific dealing year, month, auction house and location (or just 
do vague search by leaving some of them blank), we will end up to get a list of auction goods that fulfill 
these requirements with their hammer price.
In searching by goods, by selecting a class, time the good is produced and the color one belongs to, we will
 get a list of the name of auction goods with url's that connect to the auction goods' original webpage.
We can also scroll down on the homepage and click any of the six pictures to go to a list of goods with 
the specific class.
Also, check out our mobile version and you will find it works well. 

Project name: Investment assistant for Chinese fine art collectors

Original Design:
Description: Our project is a Chinese fine arts auction information search engine that can be used to search for any specific type of Chinese fine art work, which has been shown on auction houses such as Sotheby's or Christies, by key words of an auction good's features. When users try to search for art works either in abstract by a single key word or with full description, all matched results should pop out, showing information containing name, lot number at a specific auction, its starndard price in US dollar, and furthermore, a URL links to the auction good for more details. 
An auction good is unique based on its URL. An auction good belongs to a certain class such as calligraphy, painting, ceramic, etc, with other characteristics like color, decoration pattern and mark. Also, it can be traced back to a unique time when it was made. An auction house is unique based on its name and location (for instance Sotheby's Hongkong is different from Sotheby's US)Knowing an auction good's price at a specific year plus both the current consumption power of the corresponding currency and that by the time when the auction took place, users should have a good sense of the market price of a piece of an art work for better assessment during antique investment. 



Modifications made for Project 2:

1. There is a new table 'Scale', which is a weak entity to AuctionGood that tells the size of a certain auction good in both general sense and detailed sense. It contains a field named ‘scope’, that has a value of a composite type called 'size', which has 5 elements: height, base, mouth, width, depth. For certain classes of goods, such as ceramic which can only be measured in terms of height, base and mouth, we leave the rest two parameters to be 0.

2. For each auction good (in table 'AuctionGood'), there is an extra field called "conditionReport", which is in TEXT type that tells the user about the condition of the auction good, in terms of excellent condition, etc. Also the field “name” in table ‘AuctionGood’ and also the field “dimensions” from table ‘scale’ are now updated to be of the type TEXT.
This modification fits the original design because we are just providing more detailed, yet essential information to users, such that people can take the condition of a certain good into consideration when evaluating the worth of the good. The “dimensions” field added to the table ‘scale’ can give people a general sense of the size of the good if the digital measures from field “scope” is not intuitive enough.
 
3. As for the type array, we already have that in both ‘Genre’’s “feature” and ‘Price’’s “estimate”. They both make sense for the following reasons: as for the field “feature” in table ‘Genre’, the contents are just discrete descriptions of the properties of goods, without any generic formatting. So we just put them in an array to accommodate the meaningful properties. As for the field “estimate” in table ‘Price’, the contents represents a range in which the actual value of the good can fall. So we provide a min and a max price, put them in an array of length two. 

Queries:

1:
select lotnum, info 
from (select a.lotnumber as lotnum, 
	a.name || ', condition: (' || a.conditionReport || ') size: (' || s.dimensions || ')' as info, 
	to_tsvector(a.name) || to_tsvector(a.conditionReport) || to_tsvector(s.dimensions) as document 
      from auctiongood a join scale s on a.url=s.url) p_search 
where p_search.document @@ to_tsquery('Excellent & medium');

Description: This query finds auction goods that have an excellent condition of medium size, and prints their lot numbers as well as a string formed by concatenating their names, conditions and sizes. The way to implement ‘have an excellent condition’ is to use full text search for the words “excellent” and “medium”, instead of putting more conditions in “where”.

 lotnum |                                                        info
--------+---------------------------------------------------------------------------------------------------------------------
    111 | A BLUE AND WHITE SQUARE DRAGONS AND FIGURES VASE, ZUN, condition: (Excellent Condition) size: (medium)
      9 | A RARE CLOISONNÉ ENAMEL AND GILT-BRONZE "DRAGON" VASE, TIANQIUPING, condition: (Excellent Condition) size: (medium)
    108 | A RARE CORAL-GROUND FAMILLE-VERTE "FLORAL" BOWL, condition: (Excellent Condition) size: (medium)
    717 | A LONGQUAN CELADON ‘TWIN-PHOENIX’ MALLET VASE, condition: (Excellent Condition) size: (medium)
(4 rows)

2:
select a.name, p.estimate 
from auctiongood a 
join price p on a.url=p.url 
where p.estimate[1]>10000 and p.estimate[2]>20000 
group by a.name, p.estimate
order by p.estimate[1];

Description: This query finds auction goods whose minimum estimated price is greater than 10000 and maximum estimated price is greater than 20000, then print their names and the corresponding range of the estimated price, ordered by the minimum estimated price in ascending order. This query accesses the array type, which is the field “estimate”.

                                        name                                        |      estimate
------------------------------------------------------------------------------------+---------------------
 A BLUE AND WHITE SQUARE DRAGONS AND FIGURES VASE, ZUN                              | {51557,77336}
 LandScape                                                                          | {51775,66568}
 A RARE CLOISONNÉ ENAMEL AND GILT-BRONZE "DRAGON" VASE, TIANQIUPING                 | {64446,90225}
 A LARGE INSCRIBED BRONZE BELL DATED QIANLONG 13TH YEAR                             | {80000,100000}
 A GILT-BRONZE FIGURE DEPICTING NGAWANG LOBSANG GYATSO, DALAI LAMA V TIBETO-CHINESE | {80000,100000}
 A SUPERBLY CARVED BAMBOO "RIVERSCAPE" BRUSHPOT BY ZHANG XIHUANG                    | {128891,193336}
 A RARE CORAL-GROUND FAMILLE-VERTE "FLORAL" BOWL                                    | {322231,386678}
 IMPERIAL KHOTAN-GREEN JADE "TAISHANG HUANGDI ZHI BAO" SEAL                         | {10311404,15467107}
(8 rows)

3:
select a.lotnumber, g.class, g.feature, (s.scope).mouth, (s.scope).height 
from genre g 
join scale s on g.url=s.url 
join auctiongood a on g.url=a.url 
where (s.scope).mouth>0 and (s.scope).height>10 
order by a.lotnumber;

Description: This query finds auction goods who has a parameter mouth (meaning not equal to 0), and a height greater than 10. Then it prints their lot number, the class they belong to, their feature which is an array, and the values of mouth and height. This query accesses the new composite type “size”, in terms of getting values of the elements mouth and height.
 
lotnumber |  class  |                                feature                                | mouth | height
-----------+---------+-----------------------------------------------------------------------+-------+--------
         9 | others  | {TianQiuPin,gilt-bronze,"cloisonne enamal",dragon,ocean}              |   3.8 |   24.0
        40 | others  | {"bamboo carve","liuqing technique",riverscape,brushpot,ZhangXihuang} |   7.8 |   10.6
       108 | ceramic | {bowl,famille-verte,floral}                                           |  18.5 |   10.9
       111 | ceramic | {"square zun",dragon,figure,lotus}                                    |  14.8 |   26.0
       707 | ceramic | {bowl,"oil spot"}                                                     |  12.2 |   10.6
       717 | ceramic | {vase,LONGQUAN,twin-phoenix}                                          |   8.7 |   27.3
(6 rows)
