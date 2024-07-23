# WebXR Graph Visualization

WebXR-based 3D Graph Visualization of GitHub Markdown files

## Description

This project creates a WebXR-based 3D graph visualization of Markdown files stored in a GitHub repository. It analyzes connections between files and presents them in an immersive 3D environment, allowing users to explore relationships between documents in virtual reality.


## Features

- Fetches Markdown files from a specified GitHub repository
- Builds a graph based on references between files
- Provides a WebXR interface for 3D visualization of the graph
- Real-time updates using WebSockets
- HTTPS support for secure connections

## Prerequisites

- Node.js (version 14 or later recommended)
- Docker (for containerized deployment)
- A GitHub repository containing Markdown files
- GitHub Personal Access Token with appropriate permissions


## Installation

1. Clone the repository:
git clone [your-repo-url] cd webxr-graph-visualization


2. Install dependencies:
npm install

## Environment Variables

Create a `.env` file in the root directory with the following variables:
PORT=8443 GITHUB_OWNER=your_github_username 
GITHUB_REPO=your_repo_name 
GITHUB_DIRECTORY=path/to/markdown/files GITHUB_ACCESS_TOKEN=your_github_personal_access_token


## Running the Application

### Using Node.js

1. Generate SSL certificates:
./generate-cert.sh


2. Start the server:
npm start


3. Access the application at `https://localhost:8443`

### Using Docker

1. Build the Docker image:
docker build -t webxr-graph .


2. Run the Docker container:
docker run -d -p 8443:8443 -v $(pwd)/processed_files:/usr/src/app/data/processed_files webxr-graph


3. Access the application at `https://localhost:8443`

Alternatively, use the provided script:
./start_docker.sh


## Project Structure

- `server.js`: Main server file
- `generate-cert.sh`: Script to generate SSL certificates
- `Dockerfile`: Docker configuration file
- `public/`: Directory for static files
- `processed_files/`: Directory for storing processed data (mounted as a volume in Docker)

## Data Storage

- Processed files are stored in `/usr/src/app/data/processed_files`
- Markdown files are stored in `/usr/src/app/data/processed_files/markdown`
- Graph data is stored in `/usr/src/app/data/processed_files/graph-data.json`


## API Endpoints

- `/graph-data`: GET request to fetch the current graph data
- `/test-github-api`: GET request to test GitHub API access


## Docker Configuration

The Dockerfile sets up the following:

- Uses Node.js 14 as the base image
- Sets the working directory to `/usr/src/app`
- Copies package.json and installs dependencies
- Installs OpenSSL for certificate generation
- Copies all project files and the .env file
- Makes the `generate-cert.sh` script executable
- Runs the certificate generation script and starts the server on container startup


## Dependencies

- express: ^4.17.1
- ws: ^8.13.0
- axios: ^0.21.1
- dotenv: ^10.0.0
- fs-extra: ^9.0.0

## Scripts

- `npm start`: Runs the server using Node.js

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the ISC License - see the [LICENSE.md](LICENSE.md) file for details.

## Author

[Your Name]

## Version

1.0.0

## Acknowledgments

- Express.js for the web server framework
- ws for WebSocket support
- axios for HTTP requests
- dotenv for environment variable management
- fs-extra for enhanced file system methods
- Docker for containerization

