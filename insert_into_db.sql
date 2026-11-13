INSERT INTO categories (id, label, icon)
SELECT 'cakes', 'Bolos', '▰'
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE id = 'cakes');

INSERT INTO categories (id, label, icon)
SELECT 'cupcakes', 'Cupcakes', '♧'
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE id = 'cupcakes');

INSERT INTO categories (id, label, icon)
SELECT 'cookies', 'Cookies', '◉'
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE id = 'cookies');

INSERT INTO categories (id, label, icon)
SELECT 'coffee', 'Cafés', '♨'
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE id = 'coffee');

INSERT INTO products (name, description, price, rating, image_url, category_id, stock)
SELECT 'Chocolate dos Sonhos',
       'Bolo de chocolate intenso com ganache aveludada.',
       89.90,
       4.9,
       'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=85',
       'cakes',
       0
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Chocolate dos Sonhos');

INSERT INTO products (name, description, price, rating, image_url, category_id, stock)
SELECT 'Delícia de Frutas Vermelhas',
       'Cheesecake cremoso com frutas frescas.',
       79.90,
       4.8,
       'https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=800&q=85',
       'cakes',
       0
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Delícia de Frutas Vermelhas');

INSERT INTO products (name, description, price, rating, image_url, category_id, stock)
SELECT 'Delícia de Cenoura',
       'Bolo de cenoura com cobertura cremosa.',
       69.90,
       4.9,
       'https://images.unsplash.com/photo-1571115177098-24ec42ed204d?auto=format&fit=crop&w=800&q=85',
       'cakes',
       0
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Delícia de Cenoura');

INSERT INTO products (name, description, price, rating, image_url, category_id, stock)
SELECT 'Cupcake de Baunilha',
       'Massa fofinha, baunilha e cobertura artesanal.',
       14.90,
       4.8,
       'https://images.unsplash.com/photo-1486427944299-d1955d23e34d?auto=format&fit=crop&w=800&q=85',
       'cupcakes',
       0
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Cupcake de Baunilha');

INSERT INTO products (name, description, price, rating, image_url, category_id, stock)
SELECT 'Cookie com Chocolate',
       'Casquinha crocante e centro macio.',
       9.90,
       4.9,
       'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=800&q=85',
       'cookies',
       0
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Cookie com Chocolate');

INSERT INTO products (name, description, price, rating, image_url, category_id, stock)
SELECT 'Cappuccino da Casa',
       'Café espresso, leite cremoso e canela.',
       12.90,
       4.7,
       'https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=800&q=85',
       'coffee',
       0
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Cappuccino da Casa');