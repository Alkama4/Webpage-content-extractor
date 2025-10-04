<template>
    <div class="webpage-details">
        <BasicCard
            class="g-a"
            icon="bx-globe"
            title="Webpage details"
            description="Inspect the details of a webpage"
        >
            <div class="flex-col gap-16">
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
                            <th>Element count</th>
                            <td>{{ elementCount }} element{{ elementCount == 1 ? '' : 's' }}</td>
                        </tr>
                        <tr>
                            <th>Data count</th>
                            <td>{{ dataCount }} datapoint{{ dataCount == 1 ? '' : 's' }}</td>
                        </tr>
                    </tbody>
                </table>
                <div class="flex-row gap-8">
                    <button class="btn-with-icon">
                        <i class="bx bxs-edit"></i>
                        <span>Edit</span>
                    </button>
                    <button class="btn-with-icon btn-danger">
                        <i class="bx bxs-trash"></i>
                        <span>Delete</span>
                    </button>
                </div>
            </div>
        </BasicCard>

        <BasicCard
            class="g-b"
            style="min-width: 500px;"
            icon="bx-list-ul"
            title="Webpage elements"
            description="Elements that are scraped from the webpage"
        >
            <div v-if="elements?.length > 0" class="entry-list-wrapper">
                <ListEntry
                    v-for="element in elements"
                    :key="element.element_id"
                    :item="element"
                    :to="`/webpages/${webpage.webpage_id}/elements/${element.element_id}`"
                    icon="bx bxs-layer"
                    labelField="metric_name"
                    subField="locator"
                    :onEdit="editElement"
                    :onDelete="deleteElement"
                />
            </div>
            <ListingPlaceholder 
                v-else
                icon="bxs-layer"
                text="No elements found"
                desc="Create a new element using the form on the right."
            />
        </BasicCard>

        <BasicCard
            class="g-c"
            icon="bx-list-plus"
            title="Setup a new element"
            description="Set up a new element to be scraped from the page"
        >
            <div class="flex-col gap-8">
                <div class="flex-col gap-8">
                    <div class="iframe-wrapper" :class="{'unloaded': !previewHtml}">
                        <iframe
                            v-if="previewHtml"
                            id="previewFrame"
                            ref="previewIframe"
                            :srcdoc="previewHtml"
                            frameborder="0"
                        ></iframe>
                        <div class="placeholder" v-else @click="loadPageToIframe">
                            <template v-if="loading.iframe">
                                <LoadingIndicator/>
                            </template>
                            <template v-else>
                                <i class="bx bx-window-open icon"></i>
                                <div class="text">Load page</div>
                                <div class="desc">Click here to fetch and display the webpage in the frame</div>
                            </template>
                        </div>
                    </div>
                </div>
                <div class="flex-col gap-8">
                    <InlineMessage 
                        :text="`Unable to parse element value as a number: ${displayeElementDetails.element.innerHTML}`"
                        :interaction="false"
                        v-if="failed.valueParse"
                    />
                    <InlineMessage 
                        :text="`Multiple elements matched (${locatorMatchCount} matches). The first element will be used.`"
                        type="warning"
                        :interaction="false"
                        v-if="locatorMatchCount > 1"
                    />
                    <InlineMessage 
                        text="A field cannot be empty" 
                        :interaction="true"
                        @close="failed.emptyFields = false"
                        v-if="failed.emptyFields"
                    />
                    <InlineMessage 
                        text="This element already exists under the webpage" 
                        :interaction="true"
                        @close="failed.alreadyExists = false"
                        v-if="failed.alreadyExists"
                    />

                    <form @submit.prevent="createElement">
                        <TextInput
                            class="f-1"
                            v-model="newElemenDetails.locator"
                            label="Locator string"
                            placeholder="div.class > section#id > ul > li:nth-of-type(3)"
                        />
                        <TextInput
                            v-model="newElemenDetails.metric_name"
                            label="Metric name"
                            placeholder="Aluminium price"
                        />
                        <button :disabled="failed.valueParse" type="submit">
                            <LoadingIndicator v-if="loading.elementCreate"/>
                            <span v-else>Create element</span>
                        </button>
                    </form>
                </div>
            </div>
        </BasicCard>

        <BasicCard
            class="g-d"
            icon="bxs-data"
            title="Scraped webpage data"
            description="Inspect the data that has been scraped from the current webpage"
        >
            <table v-if="data?.length > 0">
                <tbody>
                    <tr>
                        <th>Data ID</th>
                        <th>Element ID</th>
                        <th>Metric</th>
                        <th>Value</th>
                        <th>Timestamp</th>
                    </tr>
                    <tr v-for="entry in data">
                        <td>{{ entry.data_id }}</td>
                        <td>{{ entry.element_id }}</td>
                        <td>{{ findMetricName(entry.element_id) }}</td>
                        <td>{{ entry.value }}</td>
                        <td>{{ formatTime(entry.created_at) }}</td>
                    </tr>
                </tbody>
            </table>
            <ListingPlaceholder 
                v-else
                icon="bxs-data"
                text="No data found"
                desc="The data scraped from the current webpage will appear here."
            />
        </BasicCard>
    </div>
</template>

<script>
import BasicCard from '@/components/BasicCard.vue';
import InlineMessage from '@/components/InlineMessage.vue';
import ListEntry from '@/components/ListEntry.vue';
import ListingPlaceholder from '@/components/ListingPlaceholder.vue';
import LoadingIndicator from '@/components/LoadingIndicator.vue';
import TextInput from '@/components/TextInput.vue';
import { fastApi } from '@/utils/fastApi';
import { getCssVar, formatTime } from '@/utils/utils';

export default {
    name: 'WebpageDetails',
    components: {
        BasicCard,
        ListEntry,
        LoadingIndicator,
        TextInput,
        InlineMessage,
        ListingPlaceholder,
    },
    data() {
        return {
            webpage: {},
            elements: [],
            data: [],

            loading: {
                iframe: false,
                validate: false,
                elementCreate: false,
            },
            failed: {
                valueParse: false,
                emptyFields: false,
                alreadyExists: false,
            },

            // Iframe stuff
            iframeLoaded: false,
            previewHtml: '',
            validationResult: null,
            locatorMatchCount: 0,
            displayeElementDetails: {
                element: null,
                locator: ''
            },
            newElemenDetails: {
                locator: '',
                metric_name: ''
            }
        }
    },
    methods: {
        async getWebpageInfo() {
            const response = await fastApi.webpages.getById(this.$route.params.webpage_id);
            if (response) {
                this.webpage = response;
            }
        },
        async getWebpageElements() {
            const response = await fastApi.webpages.elements.get(this.$route.params.webpage_id);
            if (response) {
                this.elements = response.sort((a, b) => a.element_id - b.element_id);
            }
        },
        async getWebpageElementData() {
            const response = await fastApi.webpages.elements.data(this.$route.params.webpage_id);
            if (response) {
                this.data = response.sort((a, b) => a.data_id - b.data_id);
            }
        },
        formatTime(time) {
            return formatTime(time);
        },
        findMetricName(elementId) {
            const element = this.elements.find(s => s.element_id === elementId);
            return element ? element.metric_name : '';
        },
        editElement() {
            alert("TBD");
        },
        async createElement() {
            if (this.newElemenDetails.locator && this.newElemenDetails.metric_name) {
                this.loading.elementCreate = true;
                try {
                    const response = await fastApi.elements.create(this.webpage.webpage_id, this.newElemenDetails)
                    if (response) {
                        await this.getWebpageElements();
                        this.newElemenDetails = {
                            locator: '',
                            metric_name: '',
                        }
                        this.iframeLoaded = false;
                        this.displayeElementDetails = {
                            locator: '',
                            element: null
                        }

                        // Clear possible hanging errors since it worked
                        this.failed.alreadyExists = false;
                        this.failed.emptyFields = false;
                    }
                } catch(e) {
                    if (e.status == 409) {
                        this.failed.alreadyExists = true;
                    }
                } finally {
                    this.loading.elementCreate = false;
                }
            } else {
                this.failed.emptyFields = true;
            }
        },
        async deleteElement(element) {
            if (confirm("Are you certain you wish to delete this webpage? This action cannot be undone!")) {
                const response = await fastApi.elements.delete(element.element_id);
                if (response) {
                    await this.getWebpageElements();
                    await this.getWebpageElementData();
                }
            }
        },
        
        ////////////// Iframe stuff //////////////
        async loadPageToIframe() {
            this.loading.iframe = true;
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
            this.loading.iframe = false;
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
                    * { 
                        cursor: pointer;
                    }
                    :hover { 
                        outline: 2px solid ${getCssVar('--color-primary-400')} !important;
                    }
                    .scraper-located-element {
                        outline: 2px solid ${getCssVar('--color-primary-500')} !important;
                    }
                `;
                doc.head.appendChild(style);

                // Disable all links
                const anchors = doc.querySelectorAll('a');
                anchors.forEach(a => a.removeAttribute('href'));

                // Click handler – store the element & locator
                doc.addEventListener('click', (e) => {
                    const target = e.target;
                    this.displayeElementDetails.element = target;
                    this.newElemenDetails.locator = this.displayeElementDetails.locator = this.buildLocator(target);

                    this.parseNumber(this.displayeElementDetails.element.innerHTML);
                });

                this.iframeLoaded = true;
            });
        },
        buildLocator(el) {
            const parts = [];
            let current = el;

            while (current && current.nodeName.toLowerCase() !== 'html') {
                if (current === document.body) break;

                const tag = current.tagName.toLowerCase();
                let part = `${tag}`;

                // add classes (filtering ignored ones)
                if (current.classList.length > 0) {
                    const allowed = Array.from(current.classList).filter(
                        cls => !['vsc-initialized'].includes(cls)
                    );
                    if (allowed.length) part += `.${allowed.join('.')}`;
                }

                // add id
                if (current.id) {
                    part += `#${current.id}`;
                }

                // add nth-of-type if needed
                const parent = current.parentElement;
                if (parent) {
                    const sameTagSiblings = Array.from(parent.children)
                        .filter(c => c.tagName === current.tagName);
                    if (sameTagSiblings.length > 1) {
                        const idx = sameTagSiblings.indexOf(current) + 1;
                        part += `:nth-of-type(${idx})`;
                    }
                }

                parts.unshift(part);
                current = current.parentElement;
            }

            return parts.join(' > ');
        },
        parseNumber(raw) {
            if (!raw) return;
            let s = raw.trim();

            // keep digits, commas, dots, spaces, plus/minus
            let cleaned = s.replace(/[^\d.,+\- ]/g, "");
            cleaned = cleaned.replace(/[\s,]/g, "");

            if (!cleaned) {
                this.failed.valueParse = true;
                return null;
            }

            let num = Number(cleaned);
            if (isNaN(num)) {
                this.failed.valueParse = true;
                return null;
            }

            this.failed.valueParse = false;
            return num;
        },
        highlightByLocator() {
            const iframe = this.$refs.previewIframe;
            if (!iframe) return;

            const doc = iframe.contentDocument || iframe.contentWindow?.document;
            if (!doc) return;

            // Remove any previous highlights that were added by us.
            const prevHighlights = doc.querySelectorAll('.scraper-located-element');
            prevHighlights.forEach(el => el.classList.remove('scraper-located-element'));

            // Find all elements that match the stored selector.
            if (!this.newElemenDetails?.locator) return;
            const matchedEls = doc.querySelectorAll(this.newElemenDetails.locator);
            if (!matchedEls.length) return;          // nothing matched

            // Highlight every match and, optionally, log how many there were.
            matchedEls.forEach(el => el.classList.add('scraper-located-element'));

            // Store the count
            this.locatorMatchCount = matchedEls.length;
        },
    },
    computed: {
        elementCount() {
            return this.elements.length;
        },
        dataCount() {
            return this.data.length;
        },
    },
    async mounted() {
        console.log("Webpage ID:", this.$route.params.webpage_id);
        await this.getWebpageInfo();
        await this.getWebpageElements();
        await this.getWebpageElementData();
    },
    watch: {
        // When the iframe content changes, re‑attach listeners
        previewHtml() {
            if (!this.iframeLoaded) this.attachIframeListener();
        },
        'newElemenDetails.locator'() {
            this.highlightByLocator();
        }
    }
}
</script>

<style scoped>
.webpage-details {
    display: grid;
    gap: 16px;
    grid-template-columns: 4fr 3fr;
    grid-template-areas:
        "a a"
        "b c"
        "d d";
}
@media (max-width: 1000px) {
    .webpage-details {
        grid-template-columns: 1fr;
            grid-template-areas:
            "a"
            "b"
            "c"
            "d";
    }
}

.iframe-wrapper {
    width: 100%;
    height: 400px;
    border-radius: var(--card-radius);
    border: 4px solid var(--color-neutral-300);
    box-sizing: border-box;
    overflow: hidden;
    transition: var(--t-fast) border-color;
}
.iframe-wrapper.unloaded:hover {
    cursor: pointer;
}    
.iframe-wrapper.unloaded:hover {
    border-color: var(--color-neutral-400);
}
iframe {
    height: 100%;
    width: 100%;
    min-width: none;
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

.iframe-wrapper .icon {
    color: var(--color-primary-400);
    font-size: var(--fs-6);
    margin-bottom: 1rem;
    padding: 8px;
    border-radius: 100px;
    background-color: var(--color-primary-100);
    transition: var(--t-slow) transform;
}
.iframe-wrapper:hover i {
    transform: translateY(-6px) scale(1.05);
}
.iframe-wrapper .text {
    font-size: var(--fs-2);
    color: var(--text-dark-secondary);
    transition: var(--t-slow) transform;
}
.iframe-wrapper .desc {
    text-align: center;
    color: var(--text-dark-tertiary);
    font-size: var(--fs-1);
    transition: var(--t-slow) transform;
}
.iframe-wrapper:hover text,
.iframe-wrapper:hover desc {
    transform: translateY(-4px);
}

.iframe-wrapper .loading-indicator {
    font-size: var(--fs-10);
    color: var(--color-primary-500);
}


.selected-element-info i {
    color: var(--color-primary-500);
    font-size: var(--fs-4);
}

.validated-icon {
    color: var(--color-success);
    font-size: var(--fs-5);
}
</style>