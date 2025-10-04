<template>
    <header>
        <div class="name">
            <router-link to="/" class="no-deco vertical-align gap-6">
                <i class="bx bxs-server"></i>
                <span>Web Scraper Dashboard</span>
            </router-link>
        </div>
        <nav class="flex-row gap-8">
            <router-link 
                v-for="link in links"
                class="btn btn-text no-deco vertical-align gap-4" 
                :to="link.path"
            >
                <i class="bx" :class="link.icon"></i>
                <span>{{ link.name }}</span>
            </router-link>
        </nav>
    </header>

    <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
            <li v-for="(crumb, index) in crumbs" :key="index" class="breadcrumb-item">
                <router-link :to="crumb.to">{{ crumb.text }}</router-link>
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
export default {
    name: 'sdfsdf',
    data() {
        return {
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
                        text += ` ${this.$route.params[lastParam]}`
                    }

                    crumbs.push({ text, to })
                }
            }

            crumbs.unshift({ text: 'Home', to: '/' })

            return crumbs
        }
    }
}
</script>

<style scoped>
header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    gap: 8px;
    background-color: hsla(0, 0%, 100%, 0.2);
    padding-inline: var(--gutter-width);
    border-bottom: 2px solid var(--color-neutral-200);
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
    color: var(--color-primary-500);
    font-size: var(--fs-4);
    font-weight: var(--fw-semibold);
}

.name i {
    font-size: var(--fs-6);
    color: var(--color-primary-500);
}

main {
    padding-bottom: 64px;
}

nav {
    overflow-x: scroll;
}

footer {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: auto;
    margin-bottom: 0;
    color: var(--color-neutral-500);
    padding: 8px;
}

.breadcrumb {
    list-style: none;
    padding: 0;
    display: flex;
    gap: 8px;
}
.breadcrumb-item::after {
    content: '/';
    margin-left: 4px;
}
.breadcrumb-item:last-child::after { 
    content: '';
}

.btn.router-link-active {
    color: var(--text-light-primary);
    background-color: var(--color-primary-500);    
}
.btn.router-link-active:hover {
    background-color: var(--color-primary-600);
}

</style>