# Platzky Redirections

## Overview

Platzky Redirections is a plugin for the Platzky framework that allows you to set up URL redirections easily. This can be useful for maintaining SEO, handling outdated URLs, or simply redirecting traffic from one part of your site to another.

## Installation

To install Platzky Redirections, you can use pip:

```sh
pip install platzky-redirections
```

### Usage


      "plugins": [
        {
          "name": "redirections",
          "config": {
            "/old-path": "/new-path"
          }
        }
      ]
