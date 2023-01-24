SELECT * FROM products;
SELECT * FROM product_type;
SELECT * FROM product_technical_data;
SELECT * FROM product_technical_data_value;

-- Получение характеристик товара (возможно)
SELECT td.name, tdv.value, tdv.product_id
FROM product_technical_data_value AS tdv
JOIN product_technical_data as td ON tdv.technical_data_id = td.id;

-- Получение тип товара
SELECT p.id, pt.name
FROM products AS p
JOIN product_type AS pt ON p.product_type_id = pt.id;

-- функция получения типа товара по его id
CREATE OR REPLACE FUNCTION type_product(id_product int)
RETURNS text AS $$
	SELECT pt.name
	FROM products AS p
	JOIN product_type AS pt ON p.product_type_id = pt.id
	WHERE p.id = id_product;
$$ LANGUAGE 'sql';

SELECT type_product('2');

-- функция получения характеристик и их значения для товара по его id
CREATE OR REPLACE FUNCTION data_value_product(id_product int)
RETURNS TABLE (
	name text,
	value text
) AS $$
DECLARE
	temp_info record;
BEGIN
	FOR temp_info IN (SELECT td.name, tdv.value, tdv.product_id
					FROM product_technical_data_value AS tdv
					JOIN product_technical_data as td ON tdv.technical_data_id = td.id
					WHERE tdv.product_id = id_product)
		LOOP
			name = temp_info.name;
			value = temp_info.value;
			RETURN NEXT;
		END LOOP;
END; $$ LANGUAGE 'plpgsql';

SELECT data_value_product(2);

-- изменение цены товара при добавлении, если есть скидка
CREATE OR REPLACE FUNCTION price_with_discount_insert()
    RETURNS trigger
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    if new.discount_id IS NOT NULL THEN
        new.price = new.price - new.price * (SELECT amount FROM discount WHERE discount.id = new.discount_id)::numeric / 100;
    END IF;
    return new;
END;
$BODY$;
CREATE TRIGGER price_with_discount_insert_trigger BEFORE INSERT  on products
for each row execute FUNCTION price_with_discount_insert(); 

-- при редактировании цены товара, если есть скидка
CREATE OR REPLACE FUNCTION price_with_discount_update()
    RETURNS trigger
    LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    if old.discount_id IS NOT NULL THEN
        new.price = new.price - new.price * (SELECT amount FROM discount WHERE discount.id = old.discount_id)::numeric / 100;
    END IF;
    return new;
END;
$BODY$;
CREATE TRIGGER price_with_discount_update_trigger 
    BEFORE UPDATE 
    ON products
    FOR EACH ROW
    EXECUTE FUNCTION price_with_discount_update();

-- Удаление продукта
CREATE OR REPLACE PROCEDURE del_product(in id_product int)
LANGUAGE 'plpgsql'
AS $$
BEGIN
	DELETE FROM products CASCADE 
	WHERE id_product = products.id;
END;
$$;

-- Посмотреть про on_delete в django
ALTER TABLE product_technical_data_value ADD FOREIGN KEY(product_id)
REFERENCES products(id) ON DELETE CASCADE;

CREATE OR REPLACE PROCEDURE del_product(in id_product int)
LANGUAGE 'plpgsql'
AS $$
BEGIN
	DELETE FROM products
	WHERE id_product = products.id;
END;
$$;

-- получение общей суммы за все товары
CREATE OR REPLACE PROCEDURE sum_count_price(inout total_price numeric DEFAULT NULL)
LANGUAGE 'plpgsql'
AS $$
BEGIN
	total_price := (SELECT SUM(count * price) FROM products);
END;
$$;

CALL sum_count_price();

-- добавление производителя
CREATE OR REPLACE PROCEDURE create_manufacturer(in name_data varchar, in country_data varchar)
LANGUAGE 'plpgsql'
AS $$
BEGIN
	INSERT INTO manufacturers (name, country)
	VALUES (name_data, country_data);
END
$$;

CALL create_manufacturer('IBM', 'Америка');