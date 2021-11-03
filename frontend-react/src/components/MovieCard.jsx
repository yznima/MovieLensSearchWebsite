import React, { Component } from 'react';
import { Card, Divider, Image, Label, Placeholder, Rating } from 'semantic-ui-react'

const TMDB_API_URL = 'api.themoviedb.org';
const TMDB_API_KEY = 'ce22fa4e67ed1c579ec0bdd43450830c';

class MovieCard extends Component {
  render() {
    return (
      <Card>
        {!this.state ?
          <Placeholder>
            <Placeholder.Image />
          </Placeholder> :
          <Image
            wrapped
            ui={false}
            src={
              !this.state.posters || this.state.posters.length == 0 ?
                "https://www.reelviews.net/resources/img/default_poster.jpg"
                : `http://image.tmdb.org/t/p/w500/${this.state.posters[0].file_path}`
            }
          />
        }
        <Card.Content>
          <Card.Header>{this.props.name}</Card.Header>
          <Divider/>
          <Card.Meta>
            <Rating icon='star' maxRating={5} rating={this.props.rating} disabled />
            <br/>
            <br/>
            {this.props.genres.map(g => <Label key={g}>{g}</Label>)}
            <br/>
            <br/>
            <a href={`https://www.imdb.com/title/tt0${this.props.imdb}`}><img src='/images/imdb_logo.png' width='30px'></img></a>
            <a href={`https://www.themoviedb.org/movie/${this.props.tmdb}`}><img src='/images/tmdb_logo.png' width='30px'></img></a>
          </Card.Meta>
          <Card.Description>
          </Card.Description>
        </Card.Content>
      </Card>
    )
  }

  componentDidMount() {
    if (TMDB_API_KEY != "") {
      fetch(`https://${TMDB_API_URL}/3/movie/${this.props.tmdb}/images?api_key=${TMDB_API_KEY}`)
        .then((res) => {
          return res.json();
        }).then((res) => {
          this.setState({ posters: res.posters });
        }).catch((err) => {
          this.setState({ err });
        });
    }
  }
}

export default MovieCard;
