<template>
    <div class="element-form flex-col gap-8">
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
                :text="`Unable to parse element value as a number: ${truncatedInnerHtml}`"
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
                :text="requestErrorMsg" 
                :interaction="true"
                @close="requestErrorMsg = ''"
                v-if="requestErrorMsg"
            />

            <form @submit.prevent="elementCreateOrUpdate">
                <TextInput
                    v-model="newElemenDetails.metric_name"
                    label="Metric name"
                    placeholder="Aluminium price"
                />
                <TextInput
                    class="f-1"
                    v-model="newElemenDetails.locator"
                    label="Locator string"
                    placeholder="div.class > section#id > ul > li:nth-of-type(3)"
                />
                <button :disabled="failed.valueParse" type="submit">
                    <LoadingIndicator v-if="loading.formSubmit"/>
                    <span v-else>{{ existingElement ? 'Update element' : 'Create element' }}</span>
                </button>
            </form>
        </div>
    </div>
</template>

<script>
import InlineMessage from './InlineMessage.vue';
import LoadingIndicator from './LoadingIndicator.vue';
import TextInput from './TextInput.vue';
import { fastApi } from '@/utils/fastApi';
import { getCssVar } from '@/utils/utils';

export default {
    name: 'ElementForm',
    data() {
        return {
            loading: {
                iframe: false,
                validate: false,
                formSubmit: false,
            },
            failed: {
                valueParse: false,
            },
            requestErrorMsg: '',

            // Iframe stuff
            previewHtml: '',
            locatorMatchCount: 0,
            selectedElement: null,
            newElemenDetails: {
                locator: '',
                metric_name: ''
            }
        }
    },
    components: {
        TextInput,
        LoadingIndicator,
        InlineMessage,
    },
    emits: ['success'],
    props: {
        webpageUrl: {
            type: URL,
            required: true
        },
        webpageId: {
            type: Number,
            required: true
        },
        existingElement: {
            type: Object,
            default: null
        }
    },
    methods: {
        //////////////// Iframe stuff ////////////////
        async loadPageToIframe() {
            this.loading.iframe = true;
            try {
                this.previewHtml = await fastApi.preview.get({
                    url: this.webpageUrl
                });

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

                if (this.newElemenDetails.locator) this.findElementsWithLocator();

                // Click handler – store the element & locator
                doc.addEventListener('click', (e) => {
                    const target = e.target;

                    // Set selected element and parse the value out of it
                    this.selectedElement = target;
                    this.parseNumber(this.selectedElement.innerHTML);

                    // Build the locator using the target, and using that locate the elements
                    // as a check that the locator works as intended.
                    this.newElemenDetails.locator = this.buildLocator(target);
                    this.findElementsWithLocator()
                });
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
        findElementsWithLocator() {
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

            // A very odd bug, where the added class is removed by the previous code if we don't wait a bit.
            setTimeout(() => {
                // Highlight every match and, optionally, log how many there were.
                matchedEls.forEach(el => el.classList.add('scraper-located-element'));
            }, 1);

            // Store the count
            this.locatorMatchCount = matchedEls.length;
        },

        //////////////// Create/Edit element ////////////////
        async elementCreateOrUpdate() {
            this.loading.formSubmit = true;
            try {
                const response = this.existingElement
                    ? await fastApi.elements.put(this.existingElement.element_id, this.newElemenDetails)
                    : await fastApi.elements.create(this.webpageId, this.newElemenDetails);

                if (response) {
                    this.$emit('success')
                    if (!this.existingElement) {
                        this.newElemenDetails = { locator: '', metric_name: '' };
                    }
                    // Wipe errors
                    this.requestErrorMsg = '';
                }
            } catch (e) {
                this.requestErrorMsg = e.response?.data?.detail?.[0]?.msg 
                    ?? e.response?.data?.detail?.detail 
                    ?? e.message
            } finally {
                this.loading.formSubmit = false
            }
        }
    },
    mounted() {
        if (this.existingElement) {
            this.newElemenDetails = {
                locator: this.existingElement.locator || '',
                metric_name: this.existingElement.metric_name || ''
            }
        }
    },
    computed: {
        truncatedInnerHtml() {
            const html = this.selectedElement?.innerHTML ?? ''
            if (html.length <= 250) return html
            return `${html.slice(0, 250)}...`
        }
    },
    watch: {
        // When the iframe content changes, re‑attach listeners
        previewHtml() {
            this.$nextTick(this.attachIframeListener);
        },
        existingElement: {
            immediate: true,
            handler(newVal) {
                if (!newVal) return
                this.newElemenDetails = {
                    locator: newVal.locator || '',
                    metric_name: newVal.metric_name || ''
                }
            }
        }
    }
}
</script>

<style scoped>
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
</style>