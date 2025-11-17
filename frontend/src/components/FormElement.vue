<template>
    <div class="form-element flex-col gap-8">
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
                <SelectInput
                    v-model="locatorMethod"
                    label="Locator style"
                    :disabled="!selectedElement"
                    :options="[
                        { label: 'Class based (readable)', value: 'buildLocator' },
                        { label: 'Nth-of-type based (exact)', value: 'buildLocatorWithNth' },
                    ]"
                />
                <button type="submit" :disabled="loading.formSubmit || failed.valueParse">
                    <LoadingIndicator :hidden="!loading.formSubmit"/>
                    <span :class="{'hidden': loading.formSubmit}">
                        {{ existingElement ? 'Update element' : 'Create element' }}
                    </span>
                </button>
            </form>
        </div>
    </div>
</template>

<script>
import InlineMessage from './InlineMessage.vue';
import LoadingIndicator from './LoadingIndicator.vue';
import SelectInput from './SelectInput.vue';
import TextInput from './TextInput.vue';
import { fastApi } from '@/utils/fastApi';
import { getCssVar } from '@/utils/utils';

export default {
    name: 'FormElement',
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
            },
            currentWebpageLocators: [],
            locatorMethod: 'buildLocator',
        }
    },
    components: {
        TextInput,
        SelectInput,
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
        },
        otherElementsOnWebpage: {
            type: Array,
            default: () => []
        }
    },
    methods: {
        //////////////// Iframe stuff ////////////////
        async loadPageToIframe() {
            this.loading.iframe = true;

            // Fetch current locators
            this.getCurrentWebpageLocators()

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
                        outline: 2px solid ${getCssVar('--color-primary-200')} !important;
                    }

                    .scraper-previous-other-elements {
                        outline: 3px dashed ${getCssVar('--color-primary-400')} !important;
                    }
                    .scraper-previous-other-elements:hover {
                        outline: 3px dashed ${getCssVar('--color-error-light')} !important;
                    }

                    .scraper-previous-current-element {
                        outline: 3px solid ${getCssVar('--color-primary-300')} !important;
                    }
                    .scraper-previous-current-element:hover {
                        outline: 3px solid ${getCssVar('--color-primary-400')} !important;
                    }

                    .scraper-located-element {
                        outline: 3px solid ${getCssVar('--color-primary-400')} !important;
                    }
                    
                    .scraper-located-element.scraper-previous-current-element:hover {
                        outline: 3px solid ${getCssVar('--color-primary-500')} !important;
                    }

                    .scraper-located-element.scraper-previous-other-elements {
                        outline: 3px solid ${getCssVar('--color-error')} !important;
                    }
                    .scraper-located-element.scraper-previous-other-elements:hover {
                        outline: 3px solid ${getCssVar('--color-error-light')} !important;
                    }
                `;
                doc.head.appendChild(style);

                if (this.newElemenDetails.locator) this.findElementsWithLocator();
                this.findExistingElements();

                // Click handler – store the element & locator
                doc.addEventListener('click', (e) => {
                    const target = e.target;
                    
                    const a = e.target.closest('a');
                    if (a) e.preventDefault();          

                    // Set selected element and parse the value out of it
                    this.selectedElement = target;
                    this.parseNumber(this.selectedElement.innerHTML);

                    // Build the locator using the target, and using that locate the elements
                    // as a check that the locator works as intended.
                    if (this.locatorMethod === 'buildLocator') {
                        this.newElemenDetails.locator = this.buildLocator(target);
                    } else {
                        this.newElemenDetails.locator = this.buildLocatorWithNth(target);
                    }
                    this.findElementsWithLocator();

                });
            });
        },
        buildLocator(el) {
            const IGNORED_CLASSES = [
                'scraper-previous-other-elements',
                'scraper-previous-current-element',
                'scraper-located-element',
                'vsc-initialized'
            ];

            function bestPart(node) {
                const tag = node.tagName.toLowerCase();
                const classes = [...node.classList].filter(c => !IGNORED_CLASSES.includes(c));
                const id = node.id && node.id.trim();
                const parent = node.parentElement;

                // If element has a unique ID, stop here — best anchor
                if (id && document.querySelectorAll(`#${id}`).length === 1) {
                    return `#${id}`;
                }

                // Try tag + class combination (but only if unique among siblings)
                if (classes.length && parent) {
                    const classSel = `${tag}.${classes.join('.')}`;
                    const siblingsMatch = [...parent.children].filter(n =>
                        n.tagName === node.tagName &&
                        classes.every(c => n.classList.contains(c))
                    );
                    if (siblingsMatch.length === 1) return classSel;
                }

                // Fallback: tag only (if it is unique among siblings)
                if (parent) {
                    const sameTag = [...parent.children].filter(n => n.tagName === node.tagName);
                    if (sameTag.length === 1) return tag;
                }

                // If not unique by class or structure, use nth-of-type
                if (parent) {
                    const sameTag = [...parent.children].filter(n => n.tagName === node.tagName);
                    const index = sameTag.indexOf(node) + 1;
                    return `${tag}:nth-of-type(${index})`;
                }

                return tag;
            }

            const parts = [];
            let cur = el;

            while (cur && cur.nodeName.toLowerCase() !== 'html' && cur !== document.body) {
                const part = bestPart(cur);
                parts.unshift(part);

                // If part is a unique ID, we can stop climbing
                if (part.startsWith('#')) break;

                cur = cur.parentElement;
            }

            return parts.join(' > ');
        },
        buildLocatorWithNth(el) {
            function getNthTag(node) {
                const tag = node.tagName.toLowerCase();
                const parent = node.parentElement;
                if (!parent) return tag;

                const siblings = [...parent.children].filter(n => n.tagName === node.tagName);
                if (siblings.length === 1) return tag;

                const index = siblings.indexOf(node) + 1;
                return `${tag}:nth-of-type(${index})`;
            }

            // Step 1: Build full path with nth-of-type
            const parts = [];
            let cur = el;
            while (cur && cur.nodeName.toLowerCase() !== 'html' && cur !== document.body) {
                parts.unshift(getNthTag(cur));
                cur = cur.parentElement;
            }
            let selector = parts.join(' > ');

            // Step 2: Try simplifying
            for (let i = 0; i < parts.length; i++) {
                if (!parts[i].includes(':nth-of-type')) continue;

                const trialParts = [...parts];
                trialParts[i] = trialParts[i].replace(/:nth-of-type\(\d+\)/, '');
                const trialSelector = trialParts.join(' > ');
                if (document.querySelectorAll(trialSelector).length === 1) {
                    parts[i] = trialParts[i]; // remove nth-of-type
                }
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
        findExistingElements() {
            const iframe = this.$refs.previewIframe;
            if (!iframe) return;

            const doc = iframe.contentDocument || iframe.contentWindow?.document;
            if (!doc) return;
            
            // Remove any previous special highlights
            const prevSpecial = doc.querySelectorAll('.scraper-previous-other-elements');
            prevSpecial.forEach(el => el.classList.remove('scraper-previous-other-elements'));

            // Highlight each locator
            this.currentWebpageLocators.forEach(locator => {
                const matchedEls = doc.querySelectorAll(locator);
                matchedEls.forEach(el => el.classList.add('scraper-previous-other-elements'));
            });

            // Find the possible current element
            if (this.newElemenDetails?.locator) {
                const matchedEls = doc.querySelectorAll(this.newElemenDetails.locator);
                matchedEls.forEach(el => {
                    el.classList.remove('scraper-previous-other-elements')
                    el.classList.add('scraper-previous-current-element')
                });
            };
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
        async getCurrentWebpageLocators() {
            const response = await fastApi.webpages.elements.get(this.webpageId);
            if (response) {
                this.currentWebpageLocators = response.map(el => el.locator).filter(Boolean);
            }
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
        },
        'newElemenDetails.locator'() {
            this.findElementsWithLocator();
        },
        locatorMethod(newVal) {
            // When the user changes the method we re‑build the current selector
            if (this.selectedElement) {
                this.newElemenDetails.locator =
                    newVal === 'buildLocator'
                        ? this.buildLocator(this.selectedElement)
                        : this.buildLocatorWithNth(this.selectedElement);
                this.findElementsWithLocator();
            }
        }
    }
}
</script>

<style scoped>
.iframe-wrapper {
    width: 100%;
    height: 50vh;
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
    position: relative;
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