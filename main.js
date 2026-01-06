const articlesList = document.querySelector(".articles-list");
const articleTemplate = document.getElementById("article-template");

function fetchArticles() {
  // Замените этот URL на адрес вашего API
  const apiUrl = "http://127.0.0.1:8000/stories";

  // fetch отправляет запрос и возвращает "обещание" (Promise), что когда-нибудь будет ответ
  return fetch(apiUrl).then((response) => {
    // Когда ответ получен, мы сначала проверяем, все ли в порядке
    if (!response.ok) {
      // Если код ответа не 200-299 (например, 404 или 500), создаем ошибку
      throw new Error(`Ошибка сети: ${response.status}`);
    }
    // response.json() тоже возвращает Promise, который преобразует ответ из JSON в объект JavaScript

    return response.json();
  });
}

function createArticleElement(articleData) {
  // 1. Клонируем содержимое шаблона. Мы получаем готовый <li> с вложенной <article>
  const articleClone = articleTemplate.content.cloneNode(true);

  // 2. Находим нужные элементы ВНУТРИ этого клона
  const titleElement = articleClone.querySelector(".article__title");
  const descriptionElement = articleClone.querySelector(
    ".article__description"
  );

  // 3. Заполняем их данными из полученного объекта
  titleElement.textContent = articleData.title;
  descriptionElement.textContent = articleData.text; // У тестового API описание в поле "body"

  // 4. Возвращаем полностью готовый и заполненный элемент
  return articleClone;
}

function main() {
  articlesList.innerHTML = "<p>Загрузка статей...</p>"; // Показываем пользователю, что что-то происходит

  fetchArticles()
    .then((articles) => {
      // Этот код выполнится, ТОЛЬКО ЕСЛИ данные успешно загрузились
      articlesList.innerHTML = ""; // Очищаем надпись "Загрузка..."

      // Для примера возьмем только первые 10 статей
      const articlesToRender = articles.slice(0, 10);

      articlesToRender.forEach((articleData) => {
        // Для каждой статьи...
        const newArticle = createArticleElement(articleData); // ...создаем элемент...
        articlesList.append(newArticle); // ...и добавляем его в список на странице.
      });
    })
    .catch((error) => {
      // Этот код выполнится, ЕСЛИ на любом из этапов в fetchArticles произошла ошибка
      console.error(error); // Выводим ошибку в консоль для отладки
      articlesList.innerHTML = `<p style="color: red;">Не удалось загрузить статьи.</p>`;
    });
}

// Это стандартный и самый правильный способ запускать JS-код.
// Код внутри выполнится только тогда, когда весь HTML-документ будет построен.
document.addEventListener("DOMContentLoaded", main);
