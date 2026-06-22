from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain
import re
import time

def run_research_pipeline(topic: str) -> dict:

    state = {}

    # -------------------------------
    # STEP 1 - SEARCH
    # -------------------------------
    print("\n" + "=" * 50)
    print("step 1 - search agent is working ...")
    print("=" * 50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Search the web using the tool and return at least 4 results with Title, URL and Summary about: {topic}")]
    })

    state["search_results"] = search_result['messages'][-1].content
    print("\nsearch result:\n", state['search_results'])

    # -------------------------------
    # STEP 2 - MULTI URL SCRAPING
    # -------------------------------
    print("\n" + "=" * 50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("=" * 50)

    reader_agent = build_reader_agent()

    # Extract URLs
    urls = list(set(re.findall(r"https?://[^\s]+", state["search_results"])))

    scraped_contents = []

    for i, url in enumerate(urls[:3]):   # limit to 2 (avoid rate limit)
        print(f"\n🔗 Scraping URL {i+1}: {url}")

        try:
            result = reader_agent.invoke({
                "messages": [("user", f"Use scrape_url tool to extract and summarize this URL:\n{url}")]
            })

            content = result['messages'][-1].content

            scraped_contents.append(
                f"Source: {url}\n{content}\n"
            )

            time.sleep(2)  # prevents rate limit

        except Exception as e:
            print(f"⚠️ Failed to scrape {url}: {e}")

    state["scraped_content"] = "\n\n".join(scraped_contents)

    print("\nScraped Content:\n", state["scraped_content"][:1000])

    # -------------------------------
    # STEP 3 - WRITER
    # -------------------------------
    print("\n" + "=" * 50)
    print("step 3 - Writer is drafting the report ...")
    print("=" * 50)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\nFinal Report:\n", state['report'])

    # -------------------------------
    # STEP 4 - CRITIC
    # -------------------------------
    print("\n" + "=" * 50)
    print("step 4 - critic is reviewing the report")
    print("=" * 50)

    state["feedback"] = critic_chain.invoke({
        "report": state['report']
    })

    print("\nCritic Report:\n", state['feedback'])

    return state


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    run_research_pipeline(topic)