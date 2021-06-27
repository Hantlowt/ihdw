<script>
	export let api;
	import { createEventDispatcher } from 'svelte';
	import { fade } from 'svelte/transition';
	import Loading from  './Loading.svelte'
	import Profile from './Profile.svelte'
	import Config from './Config.svelte'
	import Pages from './Pages.svelte'
	import Content from './Content.svelte'

	
	let pages = [
	{'name': 'Pages', 'component': Pages},
	{'name': 'Content', 'component': Content},
	{'name': 'Profile', 'component': Profile},
	{'name': 'Config', 'component': Config}];

	let selectedPage = pages[0];

	const dispatch = createEventDispatcher();

	async function disconnect() {
		api.disconnect()
		dispatch('disconnect')
	}

</script>

<header>
	<nav>
            <a href="/">Admin</a>
            <ul>
            	{#each pages as page, i}
            		<li>
            			{#if page == selectedPage}
            				{page.name}
            			{:else}
            				<a href="#" on:click={() => selectedPage = pages[i]}>{page.name}</a>
            			{/if}
            		</li>
            	{/each}
                <li><a href="#" on:click={disconnect}>Disconnect</a></li>
            </ul>
        </nav>
</header>

<main>
		<svelte:component api={api} this={selectedPage.component}/>
</main>