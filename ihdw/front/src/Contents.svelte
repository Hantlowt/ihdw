<script>
import Content from "./Content.svelte"
export let api;
let contents = []
let choose_mode = 0;
let categoriesP;
let cat_selected = '';
let cat_search_selected = '';
let searchResult = []
let searchIndex = 0;
let searchPageMax = 0;
$: categoriesP = api ? api.getCategories() : null;

async function setSearchIndex(i) {
	if (i+1 >= 1 && i+1 <= searchPageMax)
		searchIndex = i;
}

async function searchByCategory() {
	if (cat_search_selected != '')
	{
		searchResult = await api.searchContent(cat_search_selected, '')
		searchPageMax = Math.ceil(searchResult.length / 5);
		searchIndex = 0;
	}
	else
	{
		searchResult = []
		searchIndex = 0;
		searchPageMax = 0;
	}
	
}

async function openContent(content) {
    if (!contents.some(e => e.id == content.id))
        contents.push(content);
        contents = contents;
}

</script>

<section>
    <aside>
        <h1>Add content</h1>
        Category :
        {#if choose_mode == 1}
        {#await categoriesP}
		Loading...
        {:then categories}
        <select bind:value={cat_selected}>
            {#each categories as cat}
            <option value={cat}>
                {cat}
            </option>
            {/each}
        </select>
        {/await}
        {/if}
        {#if choose_mode == 2}
        <input type="text" bind:value={cat_selected}  placeholder="Name" />
        {/if}
        {#if choose_mode == 0}<a on:click={()=>choose_mode=1} href="#">Choose existant category</a> / <a on:click={()=>{choose_mode=2; cat_selected=''}} href="#">Add a new one</a>
        {:else}
        <a on:click={()=>choose_mode=0} href="#">Cancel</a>
        <button>Add</button>
        {/if}
    </aside>
    <aside>
        <h1>Search content</h1>
        {#await categoriesP}
		Loading...
        {:then categories}
        <select bind:value={cat_search_selected} on:blur={searchByCategory}>
			<option value=''>
            </option>
            {#each categories as cat}
            <option value={cat}>
                {cat}
            </option>
            {/each}
        </select>
        {/await}
		{#if searchResult.length > 0}
		{#each searchResult.slice(searchIndex*5, searchIndex*5+5) as search}
		<ul>
		<li><a href="#" on:click="{openContent(search)}">{search.preview_name} - {search.preview_data}</a></li>
		</ul>
		{/each}
		<a href="#" on:click="{setSearchIndex(searchIndex-1)}">&lt;&lt;</a> {searchIndex+1} / {searchPageMax} <a href="#" on:click="{setSearchIndex(searchIndex+1)}">&gt;&gt;</a>
		{/if}
    </aside>
</section>
<hr>
<section>
{#each contents as content}
     <Content api={api} id={content.id} category={content.category} />
{/each}
</section>