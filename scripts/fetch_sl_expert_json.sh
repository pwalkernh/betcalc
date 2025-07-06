#!/bin/bash

# =============================================================================
# Expert Data Fetcher
# =============================================================================
# 
# This script fetches expert picks using the Sportsline betting API.
# Executes a curl request to the API and writes the response (JSON) to stdout.
# 
# USAGE:
#   ./fetch_sl_expert_json.sh --expert <expertId> [OPTIONS]
# 
# REQUIRED ARGUMENTS:
#   --expert <expertId>     The unique identifier for the expert
# 
# OPTIONAL ARGUMENTS:
#   --leagues <leagues>     Comma-separated list of leagues to filter by
#                           Example: "NFL,NBA,MLB"
#   --after <cursor>        Base64 encoded cursor for pagination
#   --count <number>        Number of picks to fetch (default: 10, max: 25)
# 
# EXAMPLES:
#   ./fetch_sl_expert_json.sh --expert "50774572"
#   ./fetch_sl_expert_json.sh --expert "50774572" --leagues "NFL,NBA" --count 20
#   ./fetch_sl_expert_json.sh --expert "50774572" --after "eyJfaWQiOiI2N2Y0NmExNy0xYzFmLTRlYjAtODI2MC0zYzAxYzVkOGVhNTQtMjk2MzcxMTAtUFJPUC1GSVJTVF81X0lOTklOR1NfSEFORElDQVAiLCJzY2hlZHVsZWREYXRlVGltZSI6IjIwMjUtMDYtMTlUMTc6MDVaIn0="
# 
# EXIT CODES:
#   0 - Success
#   1 - Invalid arguments or missing required parameters
#   2 - API request failed
#   3 - Invalid response format
# 
# =============================================================================

# Sample API call.  This example fetches the next 5 MLB picks after the cursor.
# curl 'https://helios.cbssports.com/' \
#   -H 'accept: */*' \
#   -H 'accept-language: en-US,en;q=0.9' \
#   -H 'authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJTcG9ydHNsaW5lIiwiaWF0IjoxNzE3Nzc0MTA2fQ.J-lRKuvKLl9I_SaEBj5Va2Apsy-RyHgxOjJa2T2k4td2ybNuz9OUyvENyKPlQL8dVjsv3P3iii-IyOmkDPF3SH_LfXbPrlAgDPLY646v_wxdbHSWJ3DD_9xtYOtAMJ7T8zmvcQLZdfubEGO2vblHacQt0d2cnQ_JLPn8cS8y25aL8Y6rw8IGs-lhWvxssZYbNqh9RggfE_vWwey2qQ_iCDuflTuu2JEdKHsKFLJgc9SgsuF8oievfgEjF9gH6oVsK1CLuOTU7XqzEayxQTx5J3WmkNi_UMjU0uyzCHcG4yydfDn6ThQma1RflGQ9emXqU_XIbLL6GtHTe8rvg56S1g' \
#   -H 'content-type: application/json' \
#   -H 'helios-client-name: sportsline-web' \
#   -H 'origin: https://www.sportsline.com' \
#   -H 'pid: undefined' \
#   -H 'priority: u=1, i' \
#   -H 'referer: https://www.sportsline.com/' \
#   --data-raw $'{"operationName":"SLUI_ExpertPicks","variables":{"isGameForecast":false,"first":5,"sortBy":[{"field":"GAME_SCHEDULED_DATE_TIME","order":"DESC"}],"filter":{"state":"PAST","leagues":["MLB"],"cbsExpertId":[50774572]},"after":"eyJfaWQiOiI2N2Y0NmExNy0xYzFmLTRlYjAtODI2MC0zYzAxYzVkOGVhNTQtMjk2MzcxMTAtUFJPUC1GSVJTVF81X0lOTklOR1NfSEFORElDQVAiLCJzY2hlZHVsZWREYXRlVGltZSI6IjIwMjUtMDYtMTlUMTc6MDVaIn0="},"query":"query SLUI_ExpertPicks($first: Int, $after: String, $sortBy: [ExpertPickSortByInput\u0021], $filter: ExpertPickFilterInput, $isGameForecast: Boolean = false) {\\n  expertPicks(first: $first, after: $after, sortBy: $sortBy, filter: $filter) {\\n    __typename\\n    totalCount\\n    pageInfo {\\n      startCursor\\n      endCursor\\n      hasNextPage\\n      __typename\\n    }\\n    edges {\\n      cursor\\n      node {\\n        id\\n        isFeatured\\n        locked\\n        createdAt\\n        resultStatus\\n        unit\\n        writeup\\n        sportsbookName\\n        expert {\\n          ...SLUI_ExpertPicks_SportslineExpert\\n          __typename\\n        }\\n        game @skip(if: $isGameForecast) {\\n          ...SLUI_ExpertPicks_Game\\n          __typename\\n        }\\n        expertStreaks {\\n          ...SLUI_ExpertPicks_ExpertStreak\\n          __typename\\n        }\\n        selection {\\n          __typename\\n          id\\n          label\\n          subLabel\\n          marketType\\n          marketTypeLabel\\n          odds\\n          side\\n          unit\\n          ... on ExpertPickSelectionGameProps {\\n            cbsMarketId\\n            team {\\n              ...SLUI_ExpertPicks_Team\\n              __typename\\n            }\\n            value\\n            __typename\\n          }\\n          ... on ExpertPickSelectionPlayerProps {\\n            cbsMarketId\\n            player {\\n              ...SLUI_ExpertPicks_Player\\n              __typename\\n            }\\n            value\\n            __typename\\n          }\\n          ... on ExpertPickSelectionStandard {\\n            team {\\n              ...SLUI_ExpertPicks_Team\\n              __typename\\n            }\\n            value\\n            __typename\\n          }\\n          ... on ExpertPickSelectionTeamProps {\\n            cbsMarketId\\n            team {\\n              ...SLUI_ExpertPicks_Team\\n              __typename\\n            }\\n            value\\n            __typename\\n          }\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n  }\\n}\\n\\nfragment SLUI_ExpertPicks_SportslineExpert on SportslineExpert {\\n  cbsExpertId\\n  firstName\\n  lastName\\n  nickName\\n  headshotUrl\\n  id\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_Game on Game {\\n  id\\n  abbrev\\n  scheduledTime\\n  homeTeamScore\\n  awayTeamScore\\n  league {\\n    ...SLUI_ExpertPicks_League\\n    __typename\\n  }\\n  awayTeam {\\n    ...SLUI_ExpertPicks_GameTeam\\n    __typename\\n  }\\n  homeTeam {\\n    ...SLUI_ExpertPicks_GameTeam\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_League on League {\\n  id\\n  abbrev\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_GameTeam on GameTeam {\\n  id\\n  abbrev\\n  nickname\\n  mediumName\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_ExpertStreak on ExpertStreak {\\n  id\\n  hot\\n  label\\n  profit\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_Team on Team {\\n  id\\n  nickname\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_Player on Player {\\n  id\\n  firstName\\n  lastName\\n  __typename\\n}"}'

# Sample API call.  This example fetches the most recent 14 picks in any sport for the expert.
# curl 'https://helios.cbssports.com/' \
#   -H 'accept: */*' \
#   -H 'accept-language: en-US,en;q=0.9' \
#   -H 'authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJTcG9ydHNsaW5lIiwiaWF0IjoxNzE3Nzc0MTA2fQ.J-lRKuvKLl9I_SaEBj5Va2Apsy-RyHgxOjJa2T2k4td2ybNuz9OUyvENyKPlQL8dVjsv3P3iii-IyOmkDPF3SH_LfXbPrlAgDPLY646v_wxdbHSWJ3DD_9xtYOtAMJ7T8zmvcQLZdfubEGO2vblHacQt0d2cnQ_JLPn8cS8y25aL8Y6rw8IGs-lhWvxssZYbNqh9RggfE_vWwey2qQ_iCDuflTuu2JEdKHsKFLJgc9SgsuF8oievfgEjF9gH6oVsK1CLuOTU7XqzEayxQTx5J3WmkNi_UMjU0uyzCHcG4yydfDn6ThQma1RflGQ9emXqU_XIbLL6GtHTe8rvg56S1g' \
#   -H 'content-type: application/json' \
#   -H 'helios-client-name: sportsline-web' \
#   -H 'origin: https://www.sportsline.com' \
#   -H 'pid: undefined' \
#   -H 'priority: u=1, i' \
#   -H 'referer: https://www.sportsline.com/' \
#   --data-raw $'{"operationName":"SLUI_ExpertPicks","variables":{"isGameForecast":false,"first":14,"sortBy":[{"field":"GAME_SCHEDULED_DATE_TIME","order":"DESC"}],"filter":{"state":"PAST","cbsExpertId":[50774572]}},"query":"query SLUI_ExpertPicks($first: Int, $after: String, $sortBy: [ExpertPickSortByInput\u0021], $filter: ExpertPickFilterInput, $isGameForecast: Boolean = false) {\\n  expertPicks(first: $first, after: $after, sortBy: $sortBy, filter: $filter) {\\n    __typename\\n    totalCount\\n    pageInfo {\\n      startCursor\\n      endCursor\\n      hasNextPage\\n      __typename\\n    }\\n    edges {\\n      cursor\\n      node {\\n        id\\n        isFeatured\\n        locked\\n        createdAt\\n        resultStatus\\n        unit\\n        writeup\\n        sportsbookName\\n        expert {\\n          ...SLUI_ExpertPicks_SportslineExpert\\n          __typename\\n        }\\n        game @skip(if: $isGameForecast) {\\n          ...SLUI_ExpertPicks_Game\\n          __typename\\n        }\\n        expertStreaks {\\n          ...SLUI_ExpertPicks_ExpertStreak\\n          __typename\\n        }\\n        selection {\\n          __typename\\n          id\\n          label\\n          subLabel\\n          marketType\\n          marketTypeLabel\\n          odds\\n          side\\n          unit\\n          ... on ExpertPickSelectionGameProps {\\n            cbsMarketId\\n            team {\\n              ...SLUI_ExpertPicks_Team\\n              __typename\\n            }\\n            value\\n            __typename\\n          }\\n          ... on ExpertPickSelectionPlayerProps {\\n            cbsMarketId\\n            player {\\n              ...SLUI_ExpertPicks_Player\\n              __typename\\n            }\\n            value\\n            __typename\\n          }\\n          ... on ExpertPickSelectionStandard {\\n            team {\\n              ...SLUI_ExpertPicks_Team\\n              __typename\\n            }\\n            value\\n            __typename\\n          }\\n          ... on ExpertPickSelectionTeamProps {\\n            cbsMarketId\\n            team {\\n              ...SLUI_ExpertPicks_Team\\n              __typename\\n            }\\n            value\\n            __typename\\n          }\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n  }\\n}\\n\\nfragment SLUI_ExpertPicks_SportslineExpert on SportslineExpert {\\n  cbsExpertId\\n  firstName\\n  lastName\\n  nickName\\n  headshotUrl\\n  id\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_Game on Game {\\n  id\\n  abbrev\\n  scheduledTime\\n  homeTeamScore\\n  awayTeamScore\\n  league {\\n    ...SLUI_ExpertPicks_League\\n    __typename\\n  }\\n  awayTeam {\\n    ...SLUI_ExpertPicks_GameTeam\\n    __typename\\n  }\\n  homeTeam {\\n    ...SLUI_ExpertPicks_GameTeam\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_League on League {\\n  id\\n  abbrev\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_GameTeam on GameTeam {\\n  id\\n  abbrev\\n  nickname\\n  mediumName\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_ExpertStreak on ExpertStreak {\\n  id\\n  hot\\n  label\\n  profit\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_Team on Team {\\n  id\\n  nickname\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_Player on Player {\\n  id\\n  firstName\\n  lastName\\n  __typename\\n}"}'
  
# Sample API call.  This example fetches the most recent 15 picks in MLB and NHL for the expert.
# curl 'https://helios.cbssports.com/' \
#   -H 'accept: */*' \
#   -H 'accept-language: en-US,en;q=0.9' \
#   -H 'authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJTcG9ydHNsaW5lIiwiaWF0IjoxNzE3Nzc0MTA2fQ.J-lRKuvKLl9I_SaEBj5Va2Apsy-RyHgxOjJa2T2k4td2ybNuz9OUyvENyKPlQL8dVjsv3P3iii-IyOmkDPF3SH_LfXbPrlAgDPLY646v_wxdbHSWJ3DD_9xtYOtAMJ7T8zmvcQLZdfubEGO2vblHacQt0d2cnQ_JLPn8cS8y25aL8Y6rw8IGs-lhWvxssZYbNqh9RggfE_vWwey2qQ_iCDuflTuu2JEdKHsKFLJgc9SgsuF8oievfgEjF9gH6oVsK1CLuOTU7XqzEayxQTx5J3WmkNi_UMjU0uyzCHcG4yydfDn6ThQma1RflGQ9emXqU_XIbLL6GtHTe8rvg56S1g' \
#   -H 'content-type: application/json' \
#   -H 'helios-client-name: sportsline-web' \
#   -H 'origin: https://www.sportsline.com' \
#   -H 'pid: L:1:usI9WxeLBebQ8%252F813HU5%252FAr%252Bk8uiIHHV6fNJZ%252Fz2rtBxW4zlqZnQreeV4%252FlzRX1n:1' \
#   -H 'priority: u=1, i' \
#   -H 'referer: https://www.sportsline.com/' \
#   --data-raw $'{"operationName":"SLUI_ExpertPicks","variables":{"isGameForecast":false,"first":15,"sortBy":[{"field":"GAME_SCHEDULED_DATE_TIME","order":"DESC"}],"filter":{"state":"PAST","leagues":["MLB","NHL"],"cbsExpertId":[51306423]}},"query":"query SLUI_ExpertPicks($first: Int, $after: String, $sortBy: [ExpertPickSortByInput\u0021], $filter: ExpertPickFilterInput, $isGameForecast: Boolean = false) {\\n  expertPicks(first: $first, after: $after, sortBy: $sortBy, filter: $filter) {\\n    __typename\\n    totalCount\\n    pageInfo {\\n      startCursor\\n      endCursor\\n      hasNextPage\\n      __typename\\n    }\\n    edges {\\n      cursor\\n      node {\\n        id\\n        isFeatured\\n        locked\\n        createdAt\\n        resultStatus\\n        unit\\n        writeup\\n        sportsbookName\\n        expert {\\n          ...SLUI_ExpertPicks_SportslineExpert\\n          __typename\\n        }\\n        game @skip(if: $isGameForecast) {\\n          ...SLUI_ExpertPicks_Game\\n          __typename\\n        }\\n        expertStreaks {\\n          ...SLUI_ExpertPicks_ExpertStreak\\n          __typename\\n        }\\n        selection {\\n          __typename\\n          id\\n          label\\n          subLabel\\n          marketType\\n          marketTypeLabel\\n          odds\\n          side\\n          unit\\n          ... on ExpertPickSelectionGameProps {\\n            cbsMarketId\\n            team {\\n              ...SLUI_ExpertPicks_Team\\n              __typename\\n            }\\n            value\\n            __typename\\n          }\\n          ... on ExpertPickSelectionPlayerProps {\\n            cbsMarketId\\n            player {\\n              ...SLUI_ExpertPicks_Player\\n              __typename\\n            }\\n            value\\n            __typename\\n          }\\n          ... on ExpertPickSelectionStandard {\\n            team {\\n              ...SLUI_ExpertPicks_Team\\n              __typename\\n            }\\n            value\\n            __typename\\n          }\\n          ... on ExpertPickSelectionTeamProps {\\n            cbsMarketId\\n            team {\\n              ...SLUI_ExpertPicks_Team\\n              __typename\\n            }\\n            value\\n            __typename\\n          }\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n  }\\n}\\n\\nfragment SLUI_ExpertPicks_SportslineExpert on SportslineExpert {\\n  cbsExpertId\\n  firstName\\n  lastName\\n  nickName\\n  headshotUrl\\n  id\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_Game on Game {\\n  id\\n  abbrev\\n  scheduledTime\\n  homeTeamScore\\n  awayTeamScore\\n  league {\\n    ...SLUI_ExpertPicks_League\\n    __typename\\n  }\\n  awayTeam {\\n    ...SLUI_ExpertPicks_GameTeam\\n    __typename\\n  }\\n  homeTeam {\\n    ...SLUI_ExpertPicks_GameTeam\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_League on League {\\n  id\\n  abbrev\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_GameTeam on GameTeam {\\n  id\\n  abbrev\\n  nickname\\n  mediumName\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_ExpertStreak on ExpertStreak {\\n  id\\n  hot\\n  label\\n  profit\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_Team on Team {\\n  id\\n  nickname\\n  __typename\\n}\\n\\nfragment SLUI_ExpertPicks_Player on Player {\\n  id\\n  firstName\\n  lastName\\n  __typename\\n}"}'

# TODO: Implement argument parsing and API calls here

# Write empty JSON object to stdout for now.
echo "{}"
