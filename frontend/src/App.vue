<template>
    <header id="height-sync-source">
        <div class="read-only-notice" v-if="readOnlyMode">
            <span>
                <strong>Notice:</strong>
                You are in read-only mode. You can view content, but cannot modify it.
            </span>
            <i 
                class="bx bx-x"
                @click="readOnlyMode = false"
            ></i>
        </div>
        <div class="nav-bar">
            <div class="name">
                <router-link to="/" class="no-deco vertical-align gap-6">
                    <i class="bx bxs-server"></i>
                    <span class="long">Web Scraper Dashboard</span>
                    <span class="short">Dashboard</span>
                </router-link>
            </div>
            <nav class="flex-row gap-8">
                <router-link 
                    v-for="(link, index) in links"
                    :key="index"
                    class="btn btn-transp nav-btn no-deco vertical-align gap-6" 
                    :to="link.path"
                >
                    <i class="bx" :class="link.icon"></i>
                    <span>{{ link.name }}</span>
                </router-link>
            </nav>
        </div>
    </header>

    <div id="height-sync-target"></div>

    <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
            <li v-for="(crumb, index) in crumbs" :key="index" class="breadcrumb-item vertical-align">
                <router-link class="btn btn-transp no-deco" :to="crumb.to">{{ crumb.text }}</router-link>
            </li>
        </ol>
    </nav>

    <main>
        <RouterView/>
    </main>

    <footer>
        Footer placeholder
    </footer>
</template>

<script>
import { READ_ONLY_MODE } from './utils/config';

export default {
    data() {
        return {
            readOnlyMode: READ_ONLY_MODE,
            links: [
                {
                    icon: 'bx-globe',
                    name: 'Webpages',
                    path: '/webpages'
                },
                {
                    icon: 'bxs-bar-chart-alt-2',
                    name: 'Data',
                    path: '/data'
                },
                {
                    icon: 'bx-time-five',
                    name: 'Scheduler',
                    path: '/scheduler'
                },
                {
                    icon: 'bxs-file',
                    name: 'Logs',
                    path: '/logs'
                }
            ]
        }
    },
    computed: {
        crumbs() {
            const crumbs = []
            let pathSoFar = ''

            const segments = this.$route.path.split('/').filter(Boolean)

            for (let i = 0; i < segments.length; i++) {
                pathSoFar += '/' + segments[i]

                const match = this.$router.getRoutes().find(r => {
                    const pattern = r.path.replace(/:\w+/g, '[^/]+')
                    const regex = new RegExp(`^${pattern}$`)
                    return regex.test(pathSoFar)
                })

                if (match) {
                    let to = match.path
                    for (const key in this.$route.params) {
                        to = to.replace(`:${key}`, this.$route.params[key])
                    }

                    // get last param for this route
                    const paramKeys = (match.path.match(/:\w+/g) || []).map(k => k.slice(1))
                    let text = match.name || segments[i]
                    if (paramKeys.length) {
                        const lastParam = paramKeys[paramKeys.length - 1]
                        text += ` #${this.$route.params[lastParam]}`
                    }

                    crumbs.push({ text, to })
                }
            }

            // crumbs.unshift({ text: 'Home', to: '/' })

            return crumbs
        },
    },
    mounted() {
        const header = document.querySelector("#height-sync-source");
        const placeholder = document.querySelector("#height-sync-target");

        if (header && placeholder) {
            const updatePlaceholder = () => {
                placeholder.style.height = `${header.offsetHeight}px`;
            };

            // Initial sync
            updatePlaceholder();

            // Watch for header size changes
            this._headerObserver = new ResizeObserver(updatePlaceholder);
            this._headerObserver.observe(header);
        }
    },
    unmounted() {
        // Disconnect observer to avoid memory leaks
        if (this._headerObserver) {
            this._headerObserver.disconnect();
        }
    }
}
</script>

<style scoped>
header  {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    display: flex;
    flex-direction: column;
    z-index: var(--z-header);
    box-shadow: var(--shadow-sm);
}
.nav-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    background: linear-gradient(135deg, hsla(0, 0%, 100%, 0.9) 0%, hsla(214, 20%, 98%, 0.9) 100%);
    padding-inline: var(--gutter-width);
    border-bottom: 1px solid var(--color-neutral-200);
    height: var(--header-height);
    backdrop-filter: blur(20px);
}

.name {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: var(--fs-3);
    white-space: nowrap;
}
.name a {
    color: var(--color-primary-600);
    font-size: var(--fs-4);
    font-weight: var(--fw-bold);
    transition: color var(--t-fast);
}
.name a:hover {
    color: var(--color-primary-700);
}

.name i {
    font-size: var(--fs-6);
    color: var(--color-primary-500);
    transition: color var(--t-fast);
}
.name:hover i {
    color: var(--color-primary-600);
}

main {
    padding: 0 0 4rem;
    max-width: max(2000px, 70vw);
    margin: 0 auto;
    width: 100%;
    box-sizing: border-box;
}

nav:not([aria-label="breadcrumb"]) {
    overflow: visible;
}

footer {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: auto;
    margin-bottom: 0;
    color: var(--color-neutral-500);
    padding: 8px;
    background: transparent;
    border: none;
    box-shadow: none;
}

nav[aria-label="breadcrumb"] {
    margin: 1rem 0 !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    box-sizing: border-box;
}

.breadcrumb {
    list-style: none;
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 0;
    align-items: center;
    background: none;
    border: none;
}

.breadcrumb-item::after {
    content: '/';
    margin-left: 8px;
    font-size: var(--fs-4);
    color: var(--color-neutral-400);
}
.breadcrumb-item:last-child::after { 
    content: '';
}
.breadcrumb-item a {
    font-size: var(--fs-1);
    white-space: nowrap;
    padding: 5px 16px;
    border-radius: 100px;
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid var(--color-neutral-300);
    box-shadow: var(--shadow-xs);
}
.breadcrumb-item a:hover {
    color: var(--text-light-primary);
    background: hsl(210, 50%, 30%);
    border-color: hsl(210, 50%, 30%);
    box-shadow: var(--shadow-sm);
}

.breadcrumb-item a.router-link-active {
    background-color: var(--color-primary-500);
    box-shadow: var(--shadow-sm);
    color: var(--text-light-primary);
    border-color: transparent;
}
.breadcrumb-item a.router-link-active:hover {
    background-color: var(--color-primary-600);
    box-shadow: var(--shadow-lg);
}


.nav-btn {
    padding: 8px 16px;
    height: 30px;
}

.nav-btn.router-link-active {
    background-color: var(--color-primary-500);
    box-shadow: var(--shadow-sm);
    color: var(--text-light-primary);
}

.nav-btn.router-link-active:hover {
    background-color: var(--color-primary-600);
    box-shadow: var(--shadow-lg);
}

@media(max-width: 800px) {
    .nav-btn i {
        font-size: var(--fs-3);
    }
    .nav-btn span {
        display: none;
    }
}

.name span.short {
    display: none;
}
@media(max-width: 550px) {
    .name span.long {
        display: none;
    }
    .name span.short {
        display: unset;
    }
}


.read-only-notice {
    background-color: var(--color-primary-500);
    color: var(--text-light-primary);

    width: 100vw;
    box-sizing: border-box;

    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;

    gap: 4px;
    padding: 8px 16px;
}
.read-only-notice i {
    font-size: var(--fs-4);
    transition: background-color var(--t-fast);
    border-radius: 100px;
    padding: 4px;
    cursor: pointer;
}
.read-only-notice i:hover {
    background-color: #ffffff34;
}
.read-only-notice ::selection {
    background: var(--text-light-primary) !important;
    color: var(--color-primary-500) !important;
}
</style>