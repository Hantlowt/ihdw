<script>
export let api;
let categories_available = [];
let cat_selected_available = '';
let categories_used = [];
let cat_selected_used = '';

let page_config = {}
let message = ''
let new_page = '';

async function getCategories() {
    if (api) {
        message = ''
        categories_available = await api.getAvailableCategories()
        categories_used = await api.getUsedCategories()
        cat_selected_used = '';
        if (new_page != '') {
            categories_used.push(new_page)
            page_config = {
                'url': '',
                'template': ''
            }
            cat_selected_used = new_page
        }
    }
}

async function onSelectCategory() {
    if (cat_selected_used != '') {
        if (cat_selected_used == new_page) {
            page_config = {
                'url': '',
                'template': ''
            }
        } else {
            page_config = await api.getPageConfig(cat_selected_used)
        }
    }
}

async function savePage() {
    api.addOrUpdatePage(cat_selected_used, page_config.url, page_config.template).then(x => {
        message = x;
        new_page = '';
        getCategories()
    }).catch(x => message = x)
}

async function deletePage() {
    message = await api.deletePage(cat_selected_used).then(x => {
        message = '';
        getCategories();
    }).catch(x => message = x)
}

$: getCategories()
</script>
<section>
    <aside>
        <h1>Add new pages</h1>
        Available categories :
        <select bind:value={cat_selected_available}>
            <option value=''>
            </option>
            {#each categories_available as cat}
            <option value={cat}>
                {cat}
            </option>
            {/each}
        </select>
        <button on:click={() => {new_page=cat_selected_available; getCategories();}}>Add</button>
    </aside>

    <aside>
        <h1>Pages</h1>
        Category :
        <select bind:value={cat_selected_used} on:blur={onSelectCategory}>
            <option value=''>
            </option>
            {#each categories_used as cat}
            <option value={cat}>
                {cat}
            </option>
            {/each}
        </select>
        {#if cat_selected_used != ''}
        URL: <input type="text" bind:value={page_config.url} />
        Template: <input type="text" bind:value={page_config.template} />
        <button on:click={savePage}>Save</button>
        <button on:click={deletePage}>Delete</button>
        <p>{message}</p>
        {/if}
    </aside>
</section>
