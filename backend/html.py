html = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <title>Фильтрация постов с query params</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 600px;
      margin: 40px auto;
    }
    input, button {
      padding: 8px;
      font-size: 16px;
      margin: 5px 0;
      width: 100%;
      box-sizing: border-box;
    }
    .post {
      border: 1px solid #ddd;
      padding: 10px;
      margin-top: 15px;
      border-radius: 4px;
    }
    .post h3 {
      margin: 0 0 5px 0;
    }
  </style>
</head>
<body>

  <h2>Фильтр постов</h2>

  <form id="filterForm">
    <input type="text" name="search" placeholder="Поиск по тексту" />
    <input type="number" name="limit" placeholder="Макс. кол-во постов" min="1" />
    <button type="submit">Применить фильтр</button>
  </form>

  <h2>Посты</h2>
  <div id="posts"></div>

  <script>
    const postsContainer = document.getElementById('posts');
    const filterForm = document.getElementById('filterForm');
    const API_URL = 'http://127.0.0.1:8000/stories';

    // Получаем параметры из URL и устанавливаем в форму
    function setFormFromUrlParams() {
      const params = new URLSearchParams(window.location.search);
      filterForm.search.value = params.get('search') || '';
      filterForm.limit.value = params.get('limit') || '';
    }

    // Строим URL API с параметрами из формы / URL
    function buildApiUrl() {
      const params = new URLSearchParams();

      const search = filterForm.search.value.trim();
      const limit = filterForm.limit.value.trim();

      if (search) params.append('search', search);
      if (limit) params.append('limit', limit);

      return API_URL + (params.toString() ? `?${params.toString()}` : '');
    }

    // Загружаем и отображаем посты
    async function loadPosts() {
      try {
        postsContainer.innerHTML = 'Загрузка...';

        const response = await fetch(buildApiUrl());
        if (!response.ok) throw new Error('Ошибка загрузки');

        const posts = await response.json();
        if (!posts.length) {
          postsContainer.innerHTML = '<p>Посты не найдены</p>';
          return;
        }

        postsContainer.innerHTML = '';
        posts.forEach(post => {
          const div = document.createElement('div');
          div.className = 'post';
          div.innerHTML = `<h3>${post.title}</h3><p>${post.text}</p>`;
          postsContainer.appendChild(div);
        });
      } catch (err) {
        postsContainer.innerHTML = `<p style="color:red;">${err.message}</p>`;
      }
    }

    // Обработка отправки формы фильтрации
    filterForm.addEventListener('submit', (event) => {
      event.preventDefault();

      // Обновляем URL без перезагрузки
      const params = new URLSearchParams();

      const search = filterForm.search.value.trim();
      const limit = filterForm.limit.value.trim();

      if (search) params.append('search', search);
      if (limit) params.append('limit', limit);

      const newUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
      history.pushState({}, '', newUrl);

      // Загружаем посты с новыми параметрами
      loadPosts();
    });

    // При загрузке страницы устанавливаем форму и грузим посты
    setFormFromUrlParams();
    loadPosts();

    // Если пользователь навигирует браузером назад/вперёд
    window.addEventListener('popstate', () => {
      setFormFromUrlParams();
      loadPosts();
    });
  </script>

</body>
</html>



"""
