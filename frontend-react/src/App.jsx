import 'semantic-ui-css/semantic.min.css';
import React, { Component } from 'react';
import { Card, Divider, Dropdown, Pagination, Search, Segment } from 'semantic-ui-react';
import MovieCard from './components/MovieCard';
import { SearchMovies, SearchTags } from './apis/search';

const PAGE_SIZE = 12

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      result: [],
      query: "",
      loading: false,
      page: {
        active: 1,
        totalCount: 0
      },
      tags: [],
      possibleTags: [],
      tagsQuery: ""
    };
  }

  dispatch = (action, payload) => {
    switch (action) {
      case "UPDATE_SEARCH_RESULT": {
        const query = this.state.query;
        const active = this.state.page.active;
        const tags = this.state.tags;
        return SearchMovies(query, tags, PAGE_SIZE, active)
          .then((json) => {
            this.setState({ result: json.result, page: { active: 1, totalCount: json.totalCount } });
          }).catch((err) => {
            this.setState({ err });
          })
      }
      case "UPDATE_TAGS": {
        const active = this.state.active;
        const query = this.state.query;
        const { tags } = payload;
        return SearchMovies(query, tags, PAGE_SIZE, active)
          .then((json) => {
            this.setState({ result: json.result, page: { active: active, totalCount: json.totalCount } });
          }).catch((err) => {
            this.setState({ err });
          })
      }
      case "UPDATE_PAGE": {
        const { active } = payload
        const query = this.state.query
        const tags = this.state.tags;
        return SearchMovies(query, tags, PAGE_SIZE, active)
          .then((json) => {
            this.setState({ result: json.result, page: { active: active, totalCount: json.totalCount } });
          }).catch((err) => {
            this.setState({ err });
          })
      }
    }
  }

  render() {
    return (
      <div style={{
        padding: '10px'
      }}>
        <div style={{
          margin: 'auto',
          width: '25%'
        }}>
          <Search size="huge"
            placeholder="Search for movies..."
            loading={this.state.loading}
            onResultSelect={(e, data) =>
              console.log(data)
            }
            onSearchChange={(e) => {
              const query = e.target.value
              this.setState({ query: query, page: { active: 1, totalCount: 1 } });
              const active = this.state.page.active;
              const tags = this.state.tags;
              this.setState({ loading: true });
              this.dispatch("UPDATE_SEARCH_RESULT")
            }}

            showNoResults={this.state.result.length == 0}
            value={this.state.query}
          />

          <Dropdown size="small"
            placeholder="Tags"
            fluid
            multiple
            selection
            search
            onSearchChange={(e) => {
              const query = e.target.value
              this.setState({ tagsQuery: query })
              if (query.length > 1 || query == 0) {
                SearchTags(query)
                  .then((json) => {
                    this.setState({ possibleTags: json.result });
                  }).catch((err) => {
                    this.setState({ err });
                  })
              }
            }}
            options={this.state.possibleTags.map(tag => {
              return {
                key: tag,
                text: tag,
                value: tag,
              }
            })}
            searchQuery={this.state.tagsQuery}
            onChange={(event, { searchQuery, value }) => {
              this.setState({ tagsQuery: searchQuery, tags: value })
              this.dispatch("UPDATE_TAGS", { tags: value });
            }}
            value={this.state.tags}
          />
          <ul>
            {this.state.tags.map(tag => <li key={tag}>{tag}</li>)}
          </ul>
        </div>
        <Divider />
        <Segment>
          <Card.Group stackable>
            {this.state ? this.state.result.map(movie => (
              <MovieCard
                key={movie.id}
                name={movie.title}
                imdb={movie.imdb}
                tmdb={movie.tmdb}
              />)) : <></>
            }
          </Card.Group>
        </Segment>
        <div style={{
          margin: 'auto',
          width: '30%'
        }}>
          <Pagination
            siblingRange={1}
            totalPages={Math.max(1, (this.state.page.totalCount / PAGE_SIZE) | 0)}
            activePage={this.state.page.active}
            disabled={(this.state.page.totalCount / PAGE_SIZE) < 1}
            onPageChange={(e, data) => {
              this.dispatch("UPDATE_PAGE", { active: data.activePage });
            }}
          />
        </div>
      </div>
    );
  }
  componentDidMount() {
    this.dispatch("UPDATE_SEARCH_RESULT");
  }
}

export default App;
