// Learn more about clients at https://docs.boundaryml.com/docs/snippets/clients/overview

client<llm> GPT4oMini {
  provider openai
  retry_policy Exponential
  options {
    model "gpt-4o-mini"
    api_key env.OPENAI_API_KEY
  }
}

client<llm> Gemini {
  provider google-ai
  retry_policy Exponential
  options {
    model "gemini-2.0-flash"
    api_key env.GEMINI_API_KEY
    generationConfig {
      temperature 0.7
      max_output_tokens 5000
    }
  }
}

client<llm> Sonnet {
  provider anthropic
  options {
    model "claude-3-7-sonnet-latest"
    api_key env.ANTHROPIC_API_KEY
  }
}


client<llm> Haiku {
  provider anthropic
  retry_policy Constant
  options {
    model "claude-3-haiku-20240307"
    api_key env.ANTHROPIC_API_KEY
  }
}

// https://docs.boundaryml.com/docs/snippets/clients/round-robin
client<llm> CustomFast {
  provider round-robin
  options {
    // This will alternate between the two clients
    strategy [GPT4oMini, Haiku]
  }
}

// https://docs.boundaryml.com/docs/snippets/clients/fallback
client<llm> OpenaiFallback {
  provider fallback
  options {
    // This will try the clients in order until one succeeds
    strategy [GPT4oMini, GPT4oMini]
  }
}

// https://docs.boundaryml.com/docs/snippets/clients/retry
retry_policy Constant {
  max_retries 3
  // Strategy is optional
  strategy {
    type constant_delay
    delay_ms 200
  }
}

retry_policy Exponential {
  max_retries 2
  // Strategy is optional
  strategy {
    type exponential_backoff
    delay_ms 300
    multiplier 1.5
    max_delay_ms 10000
  }
}