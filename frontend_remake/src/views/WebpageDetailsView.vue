<template>
    <div class="webpage-details container-wrapper">
        <BasicCard
            class="f-2"
            icon="bx-globe"
            title="Webpage details"
            description="Inspect the details of a webpage"
        >
            <table>
                <tbody>
                    <tr>
                        <th>Name</th>
                        <td>{{ webpage.page_name }}</td>
                    </tr>
                    <tr>
                        <th>URL</th>
                        <td><a :href="webpage.url">{{ webpage.url }}</a></td>
                    </tr>
                    <tr>
                        <th>Scrape count</th>
                        <td>{{ scrapeCount }} scrapes</td>
                    </tr>
                    <tr>
                        <th>Data count</th>
                        <td>{{ dataCount }} datapoints</td>
                    </tr>
                </tbody>
            </table>
        </BasicCard>

        <BasicCard
            class="f-2"
            style="min-width: 500px;"
            icon="bx-target-lock"
            title="Webpage scrapes"
            description="Elements that are scraped from the webpage"
        >
            <div class="entry-list-wrapper">
                <ListEntry
                    v-for="scrape in scrapes"
                    :key="scrape.scrape_id"
                    :item="scrape"
                    :to="`/scrapes/${scrape.scrape_id}`"
                    icon="bx bx-target-lock"
                    labelField="metric_name"
                    subField="locator"
                    :onEdit="editScrape"
                    :onDelete="deleteScrape"
                />
            </div>
        </BasicCard>

        <BasicCard
            class="container-lg"
            icon="bx-list-plus"
            title="Create a scrape"
            description="Set up a new scrape for the page"
        >
            <div class="flex-cl gap-16">
                <div class="iframe-wrapper">
                    <iframe
                        v-if="previewHtml"
                        id="previewFrame"
                        ref="previewIframe"
                        :srcdoc="previewHtml"
                        frameborder="0"
                    ></iframe>
                    <div class="placeholder" v-else>
                        <i class="bx bx-globe"></i>
                        <div class="text">Page not loaded</div>
                        <div class="desc">In order to select an element, please load the page with the button below.</div>
                    </div>
                </div>
                <button @click="loadPageToIframe">Load page</button>
                <hr class="section-separator">
                <div>
                    <div class="selected-element-info">
                        <div class="vertical-align gap-4">
                            <i class="bx bxs-info-circle"></i>
                            <span>Selected elements details</span>
                        </div>
                        <table>
                            <tbody>
                                <tr>
                                    <th>Element</th>
                                    <td>{{ clickedElement?.localName || '-' }}</td>
                                </tr>
                                <tr>
                                    <th>Inner HTML</th>
                                    <td>{{ clickedElement?.innerHTML || '-' }}</td>
                                </tr>
                                <tr>
                                    <th>Parsed value</th>
                                    <td>{{ parseNumber(clickedElement?.innerHTML) || '-' }}</td>
                                </tr>
                                <tr>
                                    <th>Locator string</th>
                                    <td>{{ locator || '-' }}</td>
                                </tr>
                            </tbody>
                        </table>
                        <button>Validate locator string</button>
                    </div>
                </div>
            </div>
        </BasicCard>

        <BasicCard
            class="f-1"
            icon="bxs-data"
            title="Scraped webpage data"
            description="Inspect the data that has been scraped from the current webpage"
        >
            <table>
                <tbody>
                    <tr>
                        <th>Data ID</th>
                        <th>Scrape ID</th>
                        <th>Metric</th>
                        <th>Value</th>
                        <th>Timestamp</th>
                    </tr>
                    <tr v-for="entry in data">
                        <td>{{ entry.data_id }}</td>
                        <td>{{ entry.scrape_id }}</td>
                        <td>{{ findMetricName(entry.scrape_id) }}</td>
                        <td>{{ entry.value }}</td>
                        <td>{{ formatTime(entry.created_at) }}</td>
                    </tr>
                </tbody>
            </table>
        </BasicCard>
    </div>
</template>

<script>
import BasicCard from '@/components/BasicCard.vue';
import ListEntry from '@/components/ListEntry.vue';
import { fastApi } from '@/utils/fastApi';

export default {
    name: 'WebpageDetails',
    components: {
        BasicCard,
        ListEntry,
    },
    data() {
        return {
            webpage: {},
            scrapes: [],
            data: [],

            // Iframe stuff
            iframeLoaded: false,
            previewHtml: '',
            clickedElement: null,
            locator: '',
        }
    },
    methods: {
        async getWebpageInfo() {
            const response = await fastApi.webpages.getById(this.$route.params.webpage_id);
            if (response) {
                this.webpage = response;
            }
        },
        async getWebpageScrapes() {
            const response = await fastApi.webpages.scrapes.get(this.$route.params.webpage_id);
            if (response) {
                this.scrapes = response.sort((a, b) => a.scrape_id - b.scrape_id);
            }
        },
        async getWebpageScrapeData() {
            const response = await fastApi.webpages.scrapes.data(this.$route.params.webpage_id);
            if (response) {
                this.data = response.sort((a, b) => a.data_id - b.data_id);
            }
        },
        formatTime(time) {
            return new Date(time).toLocaleString("fi-FI", {
                year: "numeric",
                month: "2-digit",
                day: "2-digit",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit"
            });
        },
        findMetricName(scrapeId) {
            const scrape = this.scrapes.find(s => s.scrape_id === scrapeId);
            return scrape ? scrape.metric_name : '';
        },
        editScrape() {
            alert("TBD");
        },
        async deleteScrape(scrape) {
            if (confirm("Are you certain you wish to delete this webpage? This action cannot be undone!")) {
                const response = await fastApi.scrapes.delete(scrape.scrape_id);
                if (response) {
                    await this.getWebpageScrapes();
                    await this.getWebpageScrapeData();
                }
            }
        },
        
        ////////////// Iframe stuff //////////////
        async loadPageToIframe() {
            try {
                this.previewHtml = await fastApi.preview.get({
                    url: this.webpage.url
                });
                this.iframeLoaded = false;

                this.$nextTick(() => {
                    this.attachIframeListener();   // ensure iframe exists
                });
            } catch (e) {
                console.error(e);
                this.previewHtml = '<p style="color:red;">Error loading preview</p>';
            }
        },
        attachIframeListener() {
            const iframe = this.$refs.previewIframe;
            if (!iframe) return;

            iframe.addEventListener('load', () => {
                const doc = iframe.contentDocument;
                if (!doc || this.iframeLoaded) return;

                // Hover outline
                const style = doc.createElement('style');
                style.textContent = `
                    * { cursor: pointer; }
                    :hover { outline: 2px solid orange !important; }
                `;
                doc.head.appendChild(style);

                // Click handler – store the element & locator
                doc.addEventListener('click', (e) => {
                    const target = e.target;
                    this.clickedElement = target;
                    this.locator = this.buildLocator(target);   // compute locator
                });

                this.iframeLoaded = true;
            });
        },
        buildLocator(el) {
            const parts = [];
            let current = el;

            while (current && current.nodeName.toLowerCase() !== 'html') {
                if (current === document.body) break;     // stop at body

                const tag = current.tagName.toLowerCase();
                let part = `${tag}`;

                // Add class selectors – join with '.' if multiple
                if (current.classList.length > 0) {
                part += `:${Array.from(current.classList).join('.')}`;
                }

                // Add id selector if present
                if (current.id) {
                part += `:${current.id}`;
                }

                // prepend so that the order is from body → target
                parts.unshift(part);
                current = current.parentElement;
            }
            return `${parts.join(' > ')}`;
        },
        parseNumber(raw) {
            if (!raw) return;
            let s = raw.trim();

            // keep digits, commas, dots, spaces, plus/minus
            let cleaned = s.replace(/[^\d.,+\- ]/g, "");
            cleaned = cleaned.replace(/[\s,]/g, "");

            if (!cleaned) {
                return null;
            }

            let num = Number(cleaned);
            if (isNaN(num)) {
                return null;
            }

            return num;
        }
    },
    computed: {
        scrapeCount() {
            return this.scrapes.length;
        },
        dataCount() {
            return this.data.length;
        }
    },
    async mounted() {
        console.log("Webpage ID:", this.$route.params.webpage_id);
        await this.getWebpageInfo();
        await this.getWebpageScrapes();
        await this.getWebpageScrapeData();
    },
    watch: {
        // When the iframe content changes, re‑attach listeners
        previewHtml() {
            if (!this.iframeLoaded) this.attachIframeListener();
        }
    }
}
</script>

<style scoped>
.iframe-wrapper {
    width: 100%;
    height: 400px;
    border-radius: var(--card-radius);
    border: 4px solid var(--color-primary-200);
    box-sizing: border-box;
    overflow: hidden;
}
iframe {
    height: 100%;
    width: 100%;
}
.iframe-wrapper .placeholder {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    width: 100%;
    padding: max(1rem, 15%);
    box-sizing: border-box;
}
.iframe-wrapper i {
    color: var(--color-primary-400);
    font-size: var(--fs-6);
    margin-bottom: 1rem;
    padding: 8px;
    border-radius: 100px;
    background-color: var(--color-primary-100);
}
.iframe-wrapper .text {
    font-size: var(--fs-2);
    color: var(--text-dark-secondary);
}
.iframe-wrapper .desc {
    text-align: center;
    color: var(--text-dark-tertiary);
    font-size: var(--fs-1);
}

.selected-element-info i {
    color: var(--color-primary-500);
    font-size: var(--fs-4);
}
</style>