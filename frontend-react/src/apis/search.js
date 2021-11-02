export function SearchMovies(query, tags, pageSize, nextPage) {
  return fetch("search/movies", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: query,
      tags: tags,
      page: {
        size: pageSize,
        next: nextPage
      }
    })
  })
    .then(response => response.json())
}

export function SearchTags(query) {
  return fetch("search/tags", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: query
    })
  })
    .then(response => response.json())
}