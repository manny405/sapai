# %%
import unittest
import numpy as np

from sapai import *
from sapai.compress import compress, decompress
from sapai.lists import Slot, SAPList

MIN = -5
MAX = 20
pet_names = list(data["pets"].keys())


class TestLists(unittest.TestCase):
    def test_empty_slot(self):
        s = Slot()
        self.assertIsNone(s.obj)
        self.assertTrue(s.empty)

        s = Slot(Slot())
        self.assertIsNone(s.obj)
        self.assertTrue(s.empty)

    def test_pet_slot(self):
        s = Slot(Pet("fish"))
        s.obj = Pet("fish")
        self.assertEqual(s.obj.state, Pet("fish").state)
        self.assertFalse(s.empty)
        s = Slot(Slot(Pet("fish")))
        self.assertEqual(s.obj.state, Pet("fish").state)
        self.assertFalse(s.empty)
        s.obj = Slot(Pet("fish"))
        self.assertEqual(s.obj.state, Pet("fish").state)
        self.assertFalse(s.empty)

    def test_state(self):
        s = Slot()
        self.assertEqual(s.state, {"type": "Slot"})
        s = Slot(Pet("fish"))
        self.assertEqual(s.state, {"type": "Slot", "obj": Pet("fish").state})

    def test_compress(self):
        s = Slot()
        compress(s)
        s = Slot(Pet("fish"))
        c = compress(s)
        test = decompress(c)
        self.assertEqual(s.state, test.state)

    def test_list_state(self):
        l = SAPList()
        self.assertEqual(l.state, SAPList.from_state(l.state).state)
        l = SAPList([Pet(pet_names[x]) for x in range(5)], nslots=5)
        self.assertEqual(l.state, SAPList.from_state(l.state).state)

    def test_internal_list_length(self):
        l = SAPList()
        self.assertEqual(len(l), 0)

        l = SAPList(nslots=5)
        self.assertEqual(len(l._slots), 5)

        for n in range(MIN, MAX):
            try:
                l = SAPList(nslots=n)
                if n < 1:
                    raise Exception(f"SAPList should fail for {n}")
            except Exception as e:
                if n > 0:
                    raise Exception(f"SAPList should work for {n}: {e}")
                continue

            self.assertEqual(len(l._slots), n)
            self.assertEqual(len([x for x in l]), n)

    def test_list_length(self):
        for i in range(0, MAX):
            items = [Pet("fish") for x in range(i)]
            l = SAPList(items)
            self.assertEqual(len(l), i)

            for n in range(1, MAX):
                l = SAPList(items)
                l.nslots = n
                if len(items) >= n:
                    ### if there were more items than slots, then the behavior
                    ###   is to only have [:n] subset of slots left
                    self.assertEqual(len(l.empty), 0)
                else:
                    ### if there were more slots than items, then len should be
                    ###   original number of items
                    self.assertEqual(len(l.empty), n - i)

    def test_setitem_list(self):
        for i in range(0, MAX):
            items = [Pet("fish") for x in range(i)]
            l = SAPList(items)
            for n in range(0, MAX):
                try:
                    l[n] = Pet("fish")
                except Exception as e:
                    if n < i:
                        raise Exception(f"Indexing should work for i={i} & n={n}: {e}")

    def test_empty_idx(self):
        rand_idx = np.arange(0, MAX).astype(int)
        rand_test_size = np.random.randint(0, high=MAX, size=(MAX,))
        rand_buffer_size = np.random.randint(0, high=MAX, size=(MAX,))
        for i, rand_size in enumerate(rand_test_size):
            list_length = int(MAX + rand_buffer_size[i])
            l = SAPList(nslots=list_length)
            fill_idx = np.random.choice(rand_idx, size=(rand_size,), replace=False)
            l[fill_idx] = [Pet("fish") for x in range(rand_size)]
            bit_set = np.ones(list_length)
            bit_set[fill_idx] = 0
            test_idx = list(np.where(bit_set == 1)[0])
            self.assertEqual(l.empty, test_idx)

    def test_left_right(self):
        for n in range(0, MAX):
            l = SAPList(nslots=MAX)
            l[n] = Pet("fish")
            test_slot, test_idx = l.leftmost
            self.assertEqual(test_idx, n)
            test_slot, test_idx = l.rightmost
            self.assertEqual(test_idx, n)

    def test_move(self):
        for n in range(0, MAX):
            l = SAPList(nslots=MAX)
            l[0] = Pet("fish")
            try:
                l.move(0, n)
            except Exception as e:
                if n != 0:
                    raise Exception(f"Move should not fail for n={n}: {e}")
            self.assertEqual(l[n].state, Slot(Pet("fish")).state)

            l = SAPList(nslots=MAX)
            l[n] = Pet("fish")
            l.move_forward(sidx=0, eidx=-1)
            self.assertEqual(l[0].state, Slot(Pet("fish")).state)

            l = SAPList(nslots=MAX)
            l[n] = Pet("fish")
            l.move_backward()
            self.assertEqual(l[-1].state, Slot(Pet("fish")).state)

        l = SAPList([Pet(pet_names[x]) for x in range(5)], nslots=5)
        ref = SAPList([Pet(pet_names[x]) for x in range(5)], nslots=5)
        l.move_forward()
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[0, 1, 2] = [Pet(pet_names[x]) for x in range(3)]
        l.move_forward()
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        l.move_forward(0, 1)
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[0, 1, 4] = [Pet(pet_names[x]) for x in range(3)]
        l.move_forward(0, 2)
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[0, 1, 4] = [Pet(pet_names[x]) for x in range(3)]
        l.move_forward(0, 3)
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[0, 1, 4] = [Pet(pet_names[x]) for x in range(3)]
        l.move_forward(1, 3)
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        l.move_forward(2, 3)
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[0, 2, 3] = [Pet(pet_names[x]) for x in range(3)]
        l.move_forward(2, 4)
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[2, 3, 4] = [Pet(pet_names[x]) for x in range(3)]
        l.move_backward()
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[1, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        l.move_backward(0, 1)
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[1, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        l.move_backward(0, 2)
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[2, 3, 4] = [Pet(pet_names[x]) for x in range(3)]
        l.move_backward(0, 3)
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[0, 3, 4] = [Pet(pet_names[x]) for x in range(3)]
        l.move_backward(1, 4)
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[0, 3, 4] = [Pet(pet_names[x]) for x in range(3)]
        l.move_backward(2, 4)
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        l.move_backward(3, 4)
        self.assertEqual(l.state, ref.state)

    def test_index(self):
        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        for idx in l.filled:
            self.assertEqual(l.get_index(l[idx]), idx)
            self.assertEqual(l.get_index(l[idx].obj), idx)

    def test_remove(self):
        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref[0] = Slot()
        l.remove(0)
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref[2] = Slot()
        l.remove(l.slots[2])
        self.assertEqual(l.state, ref.state)

        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref = SAPList(nslots=5)
        ref[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        ref[4] = Slot()
        l.remove(l.slots[4].obj)
        self.assertEqual(l.state, ref.state)

    def test_front_and_behind(self):
        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        self.assertEqual(l.get_infront(l[0]), [])
        self.assertEqual(l.get_infront(l[1]), [l[0]])
        self.assertEqual(l.get_infront(l[1], n=2), [l[0]])
        self.assertEqual(l.get_infront(l[2], n=2), [l[1], l[0]])
        self.assertEqual(l.get_infront(l[4], n=4), [l[3], l[2], l[1], l[0]])

        self.assertEqual(l.get_behind(l[4]), [])
        self.assertEqual(l.get_behind(l[0]), [l[1]])
        self.assertEqual(l.get_behind(l[0], 2), [l[1], l[2]])
        self.assertEqual(l.get_behind(l[0], 4), [l[1], l[2], l[3], l[4]])
        self.assertEqual(l.get_behind(l[1], 2), [l[2], l[3]])
        self.assertEqual(l.get_behind(l[3], 2), [l[4]])

    def test_append(self):
        l = SAPList(nslots=5)
        l[0, 2, 4] = [Pet(pet_names[x]) for x in range(3)]
        l.append(Pet(pet_names[3]))
        self.assertEqual(l[1].obj.state, Pet(pet_names[3]).state)

        l.append(Pet(pet_names[4]))
        self.assertEqual(l[3].obj.state, Pet(pet_names[4]).state)

        self.assertRaises(Exception, l.append, Pet(pet_names[5]))


# %%

# test = TestLists()
# test.test_remove()

# %%
