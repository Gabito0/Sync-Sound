const path = window.location.pathname;
const activePage = path.substring(1);

/**
 * Set the active_page variable for Jinja templating
 *
 */
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".nav-link").forEach(function (navLink) {
    if (navLink.getAttribute("href").slice(1) === activePage) {
      navLink.classList.add("active");
    }
  });
});

/**
 * Spotify IframeApi
 *
 */
window.onSpotifyIframeApiReady = (IFrameAPI) => {
  const element = document.getElementById("embed-iframe");
  console.log(element);
  const options = {
    width: "100%",
    height: "120",
  };
  const callback = (EmbedController) => {
    const firstSong = document.querySelector("a[data-song]");
    if (firstSong) {
      const firstSongUri = firstSong.getAttribute("data-uri");
      if (firstSongUri) {
        EmbedController.loadUri(firstSongUri);
      }
    }
    EmbedController.addListener("ready", () => {
      console.log("The Embed has initialized");
      // if you change the querySelectorAll to a it will work for anchors
      // if changed to button will work for buttons
      document.querySelectorAll("a[data-song]").forEach((song) => {
        song.addEventListener("click", (e) => {
          e.preventDefault();
          console.log("clicked");
          const spotifyUri = song.getAttribute("data-uri");
          EmbedController.loadUri(spotifyUri);
        });
      });
    });
  };
  IFrameAPI.createController(element, options, callback);
};

/**
 * PUT method
 */

document.addEventListener("DOMContentLoaded", function () {
  const profileForm = document.getElementById("profileForm");

  if (profileForm) {
    profileForm.addEventListener("submit", async function (event) {
      event.preventDefault();

      let formData = new FormData(this);
      let data = {};

      formData.forEach((value, key) => {
        data[key] = value;
      });

      try {
        let response = await axios.put("/profile", data);
        if (response.data.success) {
          window.location.href = "/profile";
        } else {
          alert(response.data.message);
        }
      } catch (error) {
        console.error("Error:", error);
        alert(
          "An error occurred while updating your profile. Please try again later."
        );
      }
    });
  }
});

/**DELETE method */

document.addEventListener("DOMContentLoaded", function () {
  const deleteBtn = document.getElementById("deleteButton");
  if (deleteBtn) {
    deleteBtn.addEventListener("click", async function (event) {
      event.preventDefault();

      const csrfToken = document.querySelector(
        'input[name="csrf_token"]'
      ).value;

      try {
        let response = await axios.delete("/profile", {
          headers: {
            "X-CSRFToken": csrfToken,
          },
        });
        if (response.data.success) {
          window.location.href = "/sign-in";
        } else {
          alert(response.data.message);
        }
      } catch (error) {
        console.error("Error:", error);
        alert(
          "An error occurred while deleting your profile. Please try again later."
        );
      }
    });
  }
});
