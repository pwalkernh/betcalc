#!/bin/bash

# Parse command-line arguments
EXPERT_ID=""
LEAGUES=""
AFTER=""
COUNT=10

while [[ $# -gt 0 ]]; do
    case $1 in
        --expert)
            EXPERT_ID="$2"
            shift 2
            ;;
        --leagues)
            LEAGUES="$2"
            shift 2
            ;;
        --after)
            AFTER="$2"
            shift 2
            ;;
        --count)
            COUNT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 --expert <expertId> [--leagues <leagues>] [--after <cursor>] [--count <number>]"
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$EXPERT_ID" ]; then
    echo "Error: --expert is required"
    exit 1
fi

if [ "$COUNT" -lt 1 ] || [ "$COUNT" -gt 25 ]; then
    echo "Error: --count must be between 1 and 25"
    exit 1
fi

# Build the filter object
FILTER='{"state":"PAST","cbsExpertId":['"$EXPERT_ID"']'
if [ -n "$LEAGUES" ]; then
    LEAGUES_ARRAY=$(echo "$LEAGUES" | sed 's/,/","/g' | sed 's/^/["/' | sed 's/$/"]/')
    FILTER="$FILTER,\"leagues\":$LEAGUES_ARRAY"
fi
FILTER="$FILTER}"

# Build variables
VARIABLES='{"isGameForecast":false,"first":'"$COUNT"'","sortBy":[{"field":"GAME_SCHEDULED_DATE_TIME","order":"DESC"}],"filter":'"$FILTER"''
if [ -n "$AFTER" ]; then
    VARIABLES="$VARIABLES,\"after\":\"$AFTER\""
fi
VARIABLES="$VARIABLES}"

# The GraphQL query (copied from the example)
QUERY='query SLUI_ExpertPicks($first: Int, $after: String, $sortBy: [ExpertPickSortByInput!], $filter: ExpertPickFilterInput, $isGameForecast: Boolean = false) {
  expertPicks(first: $first, after: $after, sortBy: $sortBy, filter: $filter) {
    __typename
    totalCount
    pageInfo {
      startCursor
      endCursor
      hasNextPage
      __typename
    }
    edges {
      cursor
      node {
        id
        isFeatured
        locked
        createdAt
        resultStatus
        unit
        writeup
        sportsbookName
        expert {
          ...SLUI_ExpertPicks_SportslineExpert
          __typename
        }
        game @skip(if: $isGameForecast) {
          ...SLUI_ExpertPicks_Game
          __typename
        }
        expertStreaks {
          ...SLUI_ExpertPicks_ExpertStreak
          __typename
        }
        selection {
          __typename
          id
          label
          subLabel
          marketType
          marketTypeLabel
          odds
          side
          unit
          ... on ExpertPickSelectionGameProps {
            cbsMarketId
            team {
              ...SLUI_ExpertPicks_Team
              __typename
            }
            value
            __typename
          }
          ... on ExpertPickSelectionPlayerProps {
            cbsMarketId
            player {
              ...SLUI_ExpertPicks_Player
              __typename
            }
            value
            __typename
          }
          ... on ExpertPickSelectionStandard {
            team {
              ...SLUI_ExpertPicks_Team
              __typename
            }
            value
            __typename
          }
          ... on ExpertPickSelectionTeamProps {
            cbsMarketId
            team {
              ...SLUI_ExpertPicks_Team
              __typename
            }
            value
            __typename
          }
        }
        __typename
      }
      __typename
    }
  }
}

fragment SLUI_ExpertPicks_SportslineExpert on SportslineExpert {
  cbsExpertId
  firstName
  lastName
  nickName
  headshotUrl
  id
  __typename
}

fragment SLUI_ExpertPicks_Game on Game {
  id
  abbrev
  scheduledTime
  homeTeamScore
  awayTeamScore
  league {
    ...SLUI_ExpertPicks_League
    __typename
  }
  awayTeam {
    ...SLUI_ExpertPicks_GameTeam
    __typename
  }
  homeTeam {
    ...SLUI_ExpertPicks_GameTeam
    __typename
  }
  __typename
}

fragment SLUI_ExpertPicks_League on League {
  id
  abbrev
  __typename
}

fragment SLUI_ExpertPicks_GameTeam on GameTeam {
  id
  abbrev
  nickname
  mediumName
  __typename
}

fragment SLUI_ExpertPicks_ExpertStreak on ExpertStreak {
  id
  hot
  label
  profit
  __typename
}

fragment SLUI_ExpertPicks_Team on Team {
  id
  nickname
  __typename
}

fragment SLUI_ExpertPicks_Player on Player {
  id
  firstName
  lastName
  __typename
}'

# Build the data-raw
DATA_RAW='{"operationName":"SLUI_ExpertPicks","variables":'"$VARIABLES"'","query":"'"$QUERY"'"}'

# Execute curl
curl 'https://helios.cbssports.com/' \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJTcG9ydHNsaW5lIiwiaWF0IjoxNzE3Nzc0MTA2fQ.J-lRKuvKLl9I_SaEBj5Va2Apsy-RyHgxOjJa2T2k4td2ybNuz9OUyvENyKPlQL8dVjsv3P3iii-IyOmkDPF3SH_LfXbPrlAgDPLY646v_wxdbHSWJ3DD_9xtYOtAMJ7T8zmvcQLZdfubEGO2vblHacQt0d2cnQ_JLPn8cS8y25aL8Y6rw8IGs-lhWvxssZYbNqh9RggfE_vWwey2qQ_iCDuflTuu2JEdKHsKFLJgc9SgsuF8oievfgEjF9gH6oVsK1CLuOTU7XqzEayxQTx5J3WmkNi_UMjU0uyzCHcG4yydfDn6ThQma1RflGQ9emXqU_XIbLL6GtHTe8rvg56S1g' \
  -H 'content-type: application/json' \
  -H 'helios-client-name: sportsline-web' \
  -H 'origin: https://www.sportsline.com' \
  -H 'pid: undefined' \
  -H 'priority: u=1, i' \
  -H 'referer: https://www.sportsline.com/' \
  --data-raw "$DATA_RAW"
